# What is remWOL-moonlight?

**remWOL-moonlight** is a project that integrates a new button directly into Moonlight that allows you to **wake your PC remotely from anywhere in the world**, with or without a VPN such as Tailscale.

<img width="450" height="450" alt="Main screen" src="assets/Main_showcase.png" style="max-width:100%;height:auto;" />
<img width="450" height="450" alt="Settings screen" src="assets/settings_showcase.png" style="max-width:100%;height:auto;" />
---

# How does it work?

This project uses a **slightly modified version of Moonlight** that adds a **Wake PC (API)** button.  
This button calls a Wake-on-LAN server directly from the Moonlight interface.

### Workflow

1. You click **Wake PC (API)** in the Moonlight fork
2. Moonlight sends a request to  
   `GET /wake/<device>?token=<your-token>` on the WOL server
3. The server sends a **UDP magic packet** to the local network
4. Your PC powers on
5. Moonlight connects and starts streaming

<img width="700" height="922" alt="Workflow" src="assets/workflow.jpeg" style="max-width:100%;height:auto;" />

---

# Requirements

- An **always-on device** on your LAN to run the WOL server (NAS, Raspberry Pi, home server, etc.)
- **Wake-on-LAN enabled in your PC BIOS** and working
- The **Moonlight fork installed on your streaming device** *(Linux AppImage only for now)*

---

# Setup guide

To configure **remWOL-moonlight**, your WOL server must be reachable from anywhere on the internet.

There are two possible approaches:

- **Tailscale VPN**
- **DuckDNS + Port Forwarding** *(recommended)*

---

> [!IMPORTANT]  
> Using **Tailscale** is recommended only if it is already your main way of accessing your gaming PC with Moonlight.  
> You can continue using your existing port-forwarded Moonlight setup regardless of whether you choose the DuckDNS method or the Tailscale method.

---

> [!WARNING]  
> Installing **Tailscale on SteamOS devices can be somewhat tedious**.  
> This guide will not cover how to install Tailscale.  
> Both the **client device and the server must be connected to the same Tailnet** to send WOL requests.

---

# [beginner-friendly-guide on how to set evrything up](guide/#beginner-friendly-guide)
