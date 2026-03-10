#!/usr/bin/env python3
"""
Wake-on-LAN HTTP API Server
Listens for HTTP requests and sends magic packets on the local network.
"""

import socket
import json
import os
import time
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from collections import defaultdict

# ─── LOGGING ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger("wol-server")

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
PORT         = int(os.environ.get("WOL_PORT", 8765))
SECRET_TOKEN = os.environ.get("WOL_TOKEN", "")
CORS_ORIGIN  = os.environ.get("WOL_CORS_ORIGIN", "")   # empty = CORS disabled

# Rate limiting: max failed attempts per IP within a time window
RATE_LIMIT_MAX    = int(os.environ.get("WOL_RATE_LIMIT_MAX", 10))
RATE_LIMIT_WINDOW = int(os.environ.get("WOL_RATE_LIMIT_WINDOW", 60))  # seconds

# Devices: loaded from WOL_DEVICES env var (JSON) or from /config/devices.json
def load_devices() -> dict:
    # 1) Try WOL_DEVICES env var: '{"pc":"AA:BB:CC:DD:EE:FF"}'
    env_devices = os.environ.get("WOL_DEVICES", "")
    if env_devices:
        try:
            return json.loads(env_devices)
        except json.JSONDecodeError:
            log.warning("WOL_DEVICES is not valid JSON, ignoring.")

    # 2) Try /config/devices.json (mounted volume)
    config_file = "/config/devices.json"
    if os.path.isfile(config_file):
        try:
            with open(config_file) as f:
                return json.load(f)
        except Exception as e:
            log.warning(f"Cannot read {config_file}: {e}")

    # 3) Fallback: empty dict
    return {}

DEVICES = load_devices()

# ─── STARTUP VALIDATION ───────────────────────────────────────────────────────
if not SECRET_TOKEN:
    log.error("WOL_TOKEN is not set! Set the WOL_TOKEN environment variable.")
    raise SystemExit(1)

if len(SECRET_TOKEN) < 16:
    log.warning("WOL_TOKEN is short (< 16 characters). Consider using a longer token.")

# ─── RATE LIMITER ─────────────────────────────────────────────────────────────
_rate_data: dict = defaultdict(lambda: {"count": 0, "window_start": 0.0})

def is_rate_limited(ip: str) -> bool:
    now = time.time()
    entry = _rate_data[ip]
    if now - entry["window_start"] > RATE_LIMIT_WINDOW:
        entry["count"] = 0
        entry["window_start"] = now
    entry["count"] += 1
    if entry["count"] > RATE_LIMIT_MAX:
        log.warning(f"Rate limit exceeded for IP {ip} ({entry['count']} attempts)")
        return True
    return False

# ─── WOL ──────────────────────────────────────────────────────────────────────
def send_magic_packet(mac_address: str) -> None:
    mac_clean = mac_address.replace(":", "").replace("-", "").replace(".", "")
    if len(mac_clean) != 12:
        raise ValueError(f"Invalid MAC address: {mac_address}")
    mac_bytes = bytes.fromhex(mac_clean)
    magic_packet = b"\xff" * 6 + mac_bytes * 16
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic_packet, ("<broadcast>", 9))
        sock.sendto(magic_packet, ("<broadcast>", 7))
    log.info(f"Magic packet sent to {mac_address}")

# ─── HTTP HANDLER ─────────────────────────────────────────────────────────────
class WolHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        log.info(f"{self.address_string()} - {format % args}")

    def send_json(self, code: int, data: dict):
        body = json.dumps(data, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        if CORS_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", CORS_ORIGIN)
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, code: int, html: str):
        body = html.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.end_headers()
        self.wfile.write(body)

    def check_auth(self) -> bool:
        """Accepts Authorization: Bearer <token> header or ?token= query param (legacy, for Moonlight)."""
        # Authorization header (preferred)
        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return _secure_compare(auth_header[7:], SECRET_TOKEN)
        # Query param ?token= (legacy — used by Moonlight fork)
        params = parse_qs(urlparse(self.path).query)
        token = params.get("token", [""])[0]
        if token:
            return _secure_compare(token, SECRET_TOKEN)
        return False

    def get_client_ip(self) -> str:
        return (
            self.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or self.address_string()
        )

    def do_OPTIONS(self):
        self.send_response(204)
        if CORS_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", CORS_ORIGIN)
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        ip = self.get_client_ip()

        if path in ("", "/"):
            self.send_html(200, get_web_ui())
            return

        if path == "/devices":
            self.send_json(200, {"devices": list(DEVICES.keys()), "count": len(DEVICES)})
            return

        if path == "/health":
            self.send_json(200, {"status": "ok", "service": "wake-on-lan"})
            return

        if path.startswith("/wake/"):
            if is_rate_limited(ip):
                self.send_json(429, {"error": "Too many attempts. Please try again later."})
                return
            if not self.check_auth():
                log.warning(f"Authentication failed from {ip}")
                self.send_json(401, {"error": "Invalid or missing token"})
                return
            device_name = path[6:]
            if device_name not in DEVICES:
                self.send_json(404, {"error": f"Device '{device_name}' not found",
                                     "available": list(DEVICES.keys())})
                return
            try:
                send_magic_packet(DEVICES[device_name])
                self.send_json(200, {"success": True, "device": device_name,
                                     "mac": DEVICES[device_name]})
            except Exception as e:
                log.error(f"WOL error: {e}")
                self.send_json(500, {"error": str(e)})
            return

        self.send_json(404, {"error": "Endpoint not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        ip = self.get_client_ip()

        if is_rate_limited(ip):
            self.send_json(429, {"error": "Too many attempts. Please try again later."})
            return

        if not self.check_auth():
            log.warning(f"Authentication failed from {ip}")
            self.send_json(401, {"error": "Invalid or missing token"})
            return

        if path == "/wake":
            length = int(self.headers.get("Content-Length", 0))
            if length > 4096:
                self.send_json(413, {"error": "Payload too large"})
                return
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
            except Exception:
                self.send_json(400, {"error": "Invalid JSON body"})
                return

            if "device" in data:
                name = data["device"]
                if name not in DEVICES:
                    self.send_json(404, {"error": f"Device '{name}' not found"})
                    return
                mac = DEVICES[name]
                send_magic_packet(mac)
                self.send_json(200, {"success": True, "device": name, "mac": mac})
                return

            if "mac" in data:
                mac = data["mac"]
                try:
                    send_magic_packet(mac)
                except ValueError as e:
                    self.send_json(400, {"error": str(e)})
                    return
                self.send_json(200, {"success": True, "mac": mac})
                return

            self.send_json(400, {"error": "Specify 'device' or 'mac' in the request body"})
            return

        self.send_json(404, {"error": "Endpoint not found"})


def _secure_compare(a: str, b: str) -> bool:
    """Constant-time string comparison to prevent timing attacks."""
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a.encode(), b.encode()):
        result |= x ^ y
    return result == 0


# ─── WEB UI ───────────────────────────────────────────────────────────────────
def get_web_ui() -> str:
    devices_js = json.dumps(list(DEVICES.keys()))
    cors_note = f"<br><small>CORS: {CORS_ORIGIN}</small>" if CORS_ORIGIN else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Wake on LAN</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');
  :root {{
    --bg: #0a0a0f; --surface: #13131a; --border: #1e1e2e;
    --accent: #00ff88; --accent2: #0088ff; --text: #e0e0f0; --muted: #6060a0;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg); color: var(--text);
    font-family: 'Space Mono', monospace; min-height: 100vh;
    display: flex; align-items: center; justify-content: center; padding: 20px;
    background-image:
      radial-gradient(ellipse at 20% 50%, rgba(0,136,255,0.05) 0%, transparent 60%),
      radial-gradient(ellipse at 80% 20%, rgba(0,255,136,0.05) 0%, transparent 60%);
  }}
  .container {{ width: 100%; max-width: 480px; }}
  .header {{ margin-bottom: 40px; text-align: center; }}
  .header h1 {{
    font-family: 'Syne', sans-serif; font-size: 2.2rem; font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }}
  .header p {{ color: var(--muted); margin-top: 8px; font-size: 0.8rem; }}
  .card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 28px; margin-bottom: 16px;
  }}
  label {{
    display: block; font-size: 0.7rem; color: var(--muted);
    letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px;
  }}
  select, input {{
    width: 100%; background: var(--bg); border: 1px solid var(--border);
    color: var(--text); font-family: 'Space Mono', monospace;
    font-size: 0.9rem; padding: 12px 16px; border-radius: 8px;
    margin-bottom: 20px; outline: none; transition: border-color 0.2s;
  }}
  select:focus, input:focus {{ border-color: var(--accent); }}
  button {{
    width: 100%; background: var(--accent); color: #000; border: none;
    font-family: 'Syne', sans-serif; font-weight: 700; font-size: 1rem;
    padding: 14px; border-radius: 8px; cursor: pointer; letter-spacing: 1px;
    transition: all 0.2s;
  }}
  button:hover {{ filter: brightness(1.1); transform: translateY(-1px); }}
  button:active {{ transform: translateY(0); }}
  button:disabled {{ background: var(--border); color: var(--muted); cursor: not-allowed; transform: none; }}
  .status {{
    padding: 14px 16px; border-radius: 8px; font-size: 0.85rem;
    margin-top: 16px; display: none; animation: fadeIn 0.3s ease;
  }}
  .status.ok {{ background: rgba(0,255,136,0.1); border: 1px solid rgba(0,255,136,0.3); color: var(--accent); }}
  .status.err {{ background: rgba(255,50,50,0.1); border: 1px solid rgba(255,50,50,0.3); color: #ff6060; }}
  .divider {{ text-align: center; color: var(--muted); font-size: 0.7rem; letter-spacing: 2px; margin: 20px 0; }}
  .endpoint {{
    background: var(--bg); border: 1px solid var(--border); border-radius: 8px;
    padding: 12px 16px; font-size: 0.75rem; color: var(--muted); word-break: break-all;
  }}
  .endpoint span {{ color: var(--accent2); }}
  @keyframes fadeIn {{ from {{ opacity:0; transform: translateY(-4px); }} to {{ opacity:1; transform: none; }} }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>⚡ Wake on LAN</h1>
    <p>Wake up your devices from anywhere{cors_note}</p>
  </div>

  <div class="card">
    <label>Authentication Token</label>
    <input type="password" id="token" placeholder="Enter your secret token..." />

    <label>Device</label>
    <select id="device">
      {"".join(f'<option value="{d}">{d}</option>' for d in DEVICES.keys()) if DEVICES else '<option value="">No devices configured</option>'}
    </select>

    <div class="divider">— or use a direct MAC address —</div>

    <label>MAC Address (optional)</label>
    <input type="text" id="mac" placeholder="AA:BB:CC:DD:EE:FF" />

    <button id="btn" onclick="wake()">⚡ WAKE UP</button>
    <div class="status" id="status"></div>
  </div>

  <div class="card">
    <label>API Reference</label>
    <div class="endpoint">
      GET <span>/wake/&lt;device&gt;</span><br>
      <small style="color:#444">Header: Authorization: Bearer &lt;TOKEN&gt;</small><br><br>
      POST <span>/wake</span><br>
      <small style="color:#444">Body: {{"device": "name"}} or {{"mac": "AA:BB:..."}}</small>
    </div>
  </div>
</div>

<script>
async function wake() {{
  const token = document.getElementById('token').value.trim();
  const device = document.getElementById('device').value;
  const mac = document.getElementById('mac').value.trim();
  const btn = document.getElementById('btn');

  if (!token) {{ showStatus('Please enter the authentication token', false); return; }}
  if (!device && !mac) {{ showStatus('Select a device or enter a MAC address', false); return; }}

  btn.disabled = true;
  btn.textContent = '⏳ Sending...';

  try {{
    const body = mac ? {{ mac }} : {{ device }};
    const res = await fetch('/wake', {{
      method: 'POST',
      headers: {{
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      }},
      body: JSON.stringify(body)
    }});
    const data = await res.json();
    showStatus(res.ok ? '✓ Magic packet sent! The device is waking up...' : '✗ ' + (data.error || 'Unknown error'), res.ok);
  }} catch(e) {{
    showStatus('✗ Network error: ' + e.message, false);
  }}

  btn.disabled = false;
  btn.textContent = '⚡ WAKE UP';
}}

function showStatus(msg, ok) {{
  const el = document.getElementById('status');
  el.textContent = msg;
  el.className = 'status ' + (ok ? 'ok' : 'err');
  el.style.display = 'block';
}}
</script>
</body>
</html>"""


# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info("=" * 50)
    log.info("  Wake-on-LAN API Server")
    log.info("=" * 50)
    log.info(f"  Port     : {PORT}")
    log.info(f"  Token    : {'*' * len(SECRET_TOKEN)} ({len(SECRET_TOKEN)} chars)")
    log.info(f"  CORS     : {CORS_ORIGIN or 'disabled'}")
    log.info(f"  Rate     : max {RATE_LIMIT_MAX} req / {RATE_LIMIT_WINDOW}s per IP")
    log.info(f"  Devices  : {len(DEVICES)} configured")
    for name, mac in DEVICES.items():
        log.info(f"    • {name}: {mac}")
    log.info("=" * 50)

    server = HTTPServer(("0.0.0.0", PORT), WolHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Server stopped.")
