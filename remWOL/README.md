# remWOL — Wake-on-LAN API Server

> A lightweight, self-hosted HTTP API server that sends Wake-on-LAN magic packets to devices on your local network.  
> Zero dependencies, single container, ready in minutes.

Built as the backend for the **Moonlight-QT WOL fork**, but it also works as a standalone service for any use case.

Moonlight fork:  
https://github.com/maggicone/moonlight-qt

---

# Cool... so what does it actually do?

remWOL is a service that allows you to send a **Wake-on-LAN request to your home devices from anywhere in the world**.

You can trigger it from any device using a simple HTTP request. No additional dependencies are required (except **Tailscale** if you use it to reach your server).

Example:

```
curl "http://<your-server>:8765/wake/<device>?token=<your-token>"
```

or

```
GET "http://<your-server>:8765/wake/<device>?token=<your-token>"
```

The server will then send a **Wake-on-LAN magic packet** to the target device on your LAN.

remWOL is designed to work together with the Moonlight fork, but it can also be used **as a standalone Wake-on-LAN API service**.

If you only want the server, skip directly to the **Installation** section.

---

# Setup Guide for Moonlight

The setup process is divided into two parts:

1. Installation  
2. Check everything is working  

---

# 1) Installation

## Option 1 — Docker Compose (Recommended)

Create a file called `docker-compose.yml`:

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
```

Replace:

- `AA:BB:CC:DD:EE:FF` with the MAC address of your PC
- `your-secret-token-here` with a secret token

Start the container:

```bash
docker compose up -d
```

Check logs:

```bash
docker compose logs -f
```

Check health:

```bash
curl http://localhost:8765/health
```

---

## Option 2 — Docker Compose with `devices.json`

Create a `devices.json` file:

```json
{
  "pc-principale": "AA:BB:CC:DD:EE:FF",
  "nas": "11:22:33:44:55:66",
  "laptop": "AA:11:BB:22:CC:33"
}
```

Compose example:

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

Start:

```bash
docker compose up -d
```

---

## Option 3 — Docker CLI

```
docker run -d \
  --name remwol-moonlight \
  --network host \
  --restart unless-stopped \
  -e WOL_TOKEN=your-secret-token-here \
  -e "WOL_DEVICES={\"pc\":\"AA:BB:CC:DD:EE:FF\"}" \
  ghcr.io/maggicone/remwol-moonlight:latest
```

Logs:

```
docker logs -f remwol-moonlight
```

Stop container:

```
docker rm -f remwol-moonlight
```

---

## Option 4 — Python (No Docker)

```
git clone https://github.com/maggicone/remWOL-moonlight.git
cd remwol-moonlight

export WOL_TOKEN=your-secret-token-here
export WOL_DEVICES='{"pc":"AA:BB:CC:DD:EE:FF"}'

python3 server.py
```

---

# 2) Check Everything Is Working

## If Using Tailscale

Connect the client device using **mobile data (4G/5G hotspot)** to ensure you are outside your local network.

Make sure both the **client device and the server are connected to the same Tailnet**.

Open in your browser:

```
http://<your-server-tailscale-ip>:8765
```

If the page loads, the server is reachable.

Try waking the PC:

```
curl "http://<your-server-tailscale-ip>:8765/wake/pc?token=your-token"
```

If the PC wakes up, the installation is working correctly.

---

## If Using DuckDNS + Port Forwarding

Connect the client device using **mobile data**.

Open:

```
http://<your-duckdns-domain>:8765
```

If the page does not load, check:

- port forwarding configuration
- DuckDNS setup
- server installation

Test Wake-on-LAN:

```
curl "http://<your-duckdns-domain>:8765/wake/pc?token=your-token"
```

If the PC wakes up, the installation was successful.

---

# API Reference

## GET /health

Health check.

```
curl http://localhost:8765/health
```

---

## GET /devices

List configured devices.

```
curl http://localhost:8765/devices
```

---

## GET /wake/<device>

Wake a configured device.

```
curl "http://localhost:8765/wake/pc?token=your-token"
```

---

## POST /wake

Wake a device by name or MAC address.

```
curl -X POST http://localhost:8765/wake \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"device": "pc"}'
```

---

# Features

- REST API to wake devices
- Token authentication
- Rate limiting protection
- Device configuration via JSON or environment variables
- Lightweight Docker container
- Zero external dependencies

---

# Requirements

- Docker (with Compose) **or** Python 3.9+
- The server must be on the **same LAN** as the devices you want to wake
- Docker must run with `network_mode: host`

---

# Moonlight-QT Integration

Example request URL:

```
http://<server-ip>:8765/wake/<device-name>?token=<your-token>
```

Example:

```
http://192.168.1.10:8765/wake/pc?token=mytoken
```

---

# Build From Source

```
git clone https://github.com/maggicone/remWOL-moonlight.git
cd remwol-moonlight

docker build -t remwol-moonlight .
docker run -d --network host -e WOL_TOKEN=mytoken remwol-moonlight
```

---

# License

MIT
