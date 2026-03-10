test
# ⚡ remWOL-moonlight

> Wake up your PC remotely and stream instantly with Moonlight.

This monorepo contains two projects that work together to let you wake your PC from anywhere and jump straight into game streaming via [Moonlight](https://moonlight-stream.org).

---

## Projects

### 🖥️ `/moonlight` — Moonlight-QT Fork
A fork of [Moonlight-QT](https://github.com/moonlight-stream/moonlight-qt) with an added **Wake PC (API)** button that calls the WOL server directly from the Moonlight interface.

No more switching apps — just open Moonlight, hit Wake, and stream.

> ⚠️ **Platform support:** currently the Moonlight fork is only available as an **AppImage for Linux**. Windows and macOS builds are not yet supported.

→ See [`/moonlight`](./moonlight) for build instructions.

---

### 🌐 `/remWOL` — Wake-on-LAN API Server
A lightweight self-hosted HTTP API server that sends Wake-on-LAN magic packets to devices on your local network. Zero dependencies, single Docker container.

→ See [`/remWOL`](./remWOL) for full documentation.

**Quick start:**
```bash
docker run -d \
  --network host \
  -e WOL_TOKEN=your-secret-token \
  -e WOL_DEVICES='{"my-pc":"AA:BB:CC:DD:EE:FF"}' \
  ghcr.io/maggicone/remwol-moonlight:latest
```

---

## How it works

```
Moonlight fork  ──→  WOL API Server  ──→  Magic Packet  ──→  Your PC wakes up
  (client)             (self-hosted)         (UDP broadcast)
```

1. You click **Wake PC** in the Moonlight fork
2. Moonlight calls `GET /wake/<device>?token=<your-token>` on the WOL server
3. The server sends a UDP magic packet on the local network
4. Your PC powers on
5. Moonlight connects and starts streaming

---

## Requirements

- An always-on device on your LAN to run the WOL server (NAS, Raspberry Pi, home server)
- Wake-on-LAN enabled in your PC's BIOS
- Moonlight fork installed on your streaming device — **Linux only (AppImage)** for now

---

## License

MIT — see [LICENSE](LICENSE)
