# ⚡ Wake-on-LAN API Server

> A lightweight, self-hosted HTTP API server that sends Wake-on-LAN magic packets to devices on your local network. Zero dependencies, single container, ready in minutes.

Built as the backend for the [Moonlight-QT WOL fork](https://github.com/maggicone/moonlight-qt), but works as a standalone service for any use case.

---

## Features

- 🌐 **REST API** — wake devices by name or raw MAC address
- 🔐 **Token authentication** — via `Authorization: Bearer` header or `?token=` query param
- 🚦 **Rate limiting** — configurable per-IP brute-force protection
- 📋 **Flexible device config** — environment variable or mounted JSON file, no rebuild needed
- 🖥️ **Built-in Web UI** — accessible directly from the browser
- 🛡️ **Security headers** — `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`
- 📝 **Structured logging** — timestamped logs with levels
- 📦 **Zero dependencies** — Python stdlib only, tiny image

---

## Requirements

- Docker (with Compose plugin) **or** Python 3.9+
- The container/host must be on the **same LAN** as the target devices (broadcast UDP)
- `network_mode: host` is required in Docker so broadcast packets reach the local network

---

## Installation

### Option 1 — Docker Compose (recommended)

**1. Create a `docker-compose.yml`:**

```yaml
services:
  remwol-moonlight:
    image: ghcr.io/maggicone/remwol-moonlight:latest
    container_name: remwol-moonlight
    restart: unless-stopped
    network_mode: host
    environment:
      - WOL_TOKEN=your-secret-token-here
      - WOL_DEVICES={"pc":"AA:BB:CC:DD:EE:FF","nas":"11:22:33:44:55:66"}
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8765/health')"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**2. Start the container:**

```bash
docker compose up -d
```

**3. Check it's running:**

```bash
docker compose logs -f
curl http://localhost:8765/health
```

---

### Option 2 — Docker Compose with devices.json file

Useful if you have many devices or prefer not to use inline JSON in env vars.

**1. Create a `devices.json` file next to your compose:**

```json
{
  "pc-principale": "AA:BB:CC:DD:EE:FF",
  "nas":           "11:22:33:44:55:66",
  "laptop":        "AA:11:BB:22:CC:33"
}
```

**2. Mount it in the compose:**

```yaml
services:
  remwol-moonlight:
    image: ghcr.io/maggicone/remwol-moonlight:latest
    container_name: remwol-moonlight
    restart: unless-stopped
    network_mode: host
    environment:
      - WOL_TOKEN=your-secret-token-here
      - PYTHONUNBUFFERED=1
    volumes:
      - ./devices.json:/config/devices.json:ro
```

```bash
docker compose up -d
```

---

### Option 3 — Docker CLI (one-liner)

```bash
docker run -d \
  --name remwol-moonlight \
  --network host \
  --restart unless-stopped \
  -e WOL_TOKEN=your-secret-token-here \
  -e "WOL_DEVICES={\"pc\":\"AA:BB:CC:DD:EE:FF\",\"nas\":\"11:22:33:44:55:66\"}" \
  -e PYTHONUNBUFFERED=1 \
  ghcr.io/maggicone/remwol-moonlight:latest
```

View logs:

```bash
docker logs -f remwol-moonlight
```

Stop and remove:

```bash
docker rm -f remwol-moonlight
```

---

### Option 4 — Python (no Docker)

```bash
git clone https://github.com/maggicone/remWOL-moonlight.git
cd remwol-moonlight

export WOL_TOKEN=your-secret-token-here
export WOL_DEVICES='{"pc":"AA:BB:CC:DD:EE:FF"}'

python3 server.py
```

> **Note:** On Linux you may need `sudo` for broadcast UDP on port 9, or configure CAP_NET_BROADCAST.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `WOL_TOKEN` | ✅ | — | Auth token (min 16 chars recommended) |
| `WOL_PORT` | ❌ | `8765` | HTTP listening port |
| `WOL_DEVICES` | ❌ | `{}` | Devices as inline JSON string |
| `WOL_CORS_ORIGIN` | ❌ | `` (disabled) | Allowed CORS origin (e.g. `https://mydomain.com`) |
| `WOL_RATE_LIMIT_MAX` | ❌ | `10` | Max failed auth attempts per window |
| `WOL_RATE_LIMIT_WINDOW` | ❌ | `60` | Rate limit window in seconds |

> If both `WOL_DEVICES` and `/config/devices.json` are present, `WOL_DEVICES` takes priority.

---

## API Reference

### `GET /health`
Health check. No auth required.

```bash
curl http://localhost:8765/health
# {"status": "ok", "service": "wake-on-lan"}
```

---

### `GET /devices`
List configured device names. No auth required.

```bash
curl http://localhost:8765/devices
# {"devices": ["pc-principale", "nas"], "count": 2}
```

---

### `GET /wake/<device>`
Wake a device by name.

```bash
# Using Authorization header (recommended)
curl -H "Authorization: Bearer your-token" \
  http://localhost:8765/wake/pc-principale

# Using query param (legacy — used by Moonlight fork)
curl "http://localhost:8765/wake/pc-principale?token=your-token"
```

---

### `POST /wake`
Wake by device name or raw MAC address.

```bash
# By device name
curl -X POST http://localhost:8765/wake \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"device": "pc-principale"}'

# By MAC address directly
curl -X POST http://localhost:8765/wake \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"mac": "AA:BB:CC:DD:EE:FF"}'
```

---

## Moonlight-QT Integration

This server is the backend for the [Moonlight-QT WOL fork](https://github.com/maggicone/moonlight-qt).

Configure the **Wake PC (API)** button with:

| Field | Value |
|---|---|
| URL | `http://<server-ip>:8765/wake/<device-name>` |
| Method | GET |
| Auth | `?token=your-token` (query param) |

Example: `http://192.168.1.10:8765/wake/pc-principale?token=your-token`

---

## Behind a Reverse Proxy

If you expose the server externally, put it behind Nginx or Cloudflare for TLS termination.

**Nginx example:**

```nginx
location /wol/ {
    proxy_pass http://127.0.0.1:8765/;
    proxy_set_header X-Forwarded-For $remote_addr;
}
```

> The server reads `X-Forwarded-For` for rate limiting, so real client IPs are tracked correctly even behind a proxy.

---

## Security Notes

- `WOL_TOKEN` is **required** — the server refuses to start without it
- Token is compared using a **constant-time algorithm** to prevent timing attacks
- `?token=` query param is supported for Moonlight compatibility — note that query params may appear in server/proxy logs; prefer the `Authorization` header for other clients
- Rate limiting blocks brute-force attempts per source IP
- CORS is **disabled by default**; enable only if needed with a specific origin via `WOL_CORS_ORIGIN`

---

## Build from Source

```bash
git clone https://github.com/maggicone/remWOL-moonlight.git
cd remwol-moonlight
docker build -t remwol-moonlight:local .
docker run -d --network host -e WOL_TOKEN=mytoken remwol-moonlight:local
```

---

## License

MIT — see [LICENSE](LICENSE)
