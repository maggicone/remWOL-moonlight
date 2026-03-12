# Beginner-Friendly Guide

-This guide provides **clear, step-by-step instructions** for anyone setting up **remWOL-Moonlight** from scratch.

-**Note**: Some steps link to external software installation guides. If you get stuck, **Google is your friend**.

-This guide also assumes you know the very basics of docker.

If you still have issues, feel free to **[open an Issue](https://github.com/maggicone/remWOL-moonlight/issues/new)** describing your problem.

## ⚠️ **IMPORTANT DISCLAIMER**

> [!WARNING]  
> **Most of this project is AI-generated code.**  
> All software in this repository is provided **"AS IS", without warranty of any kind**.  
> The author is **not responsible** for any damage, data loss, or issues caused by following this guide or using the software.

wthout further ado, let's get started

------

# Requirements

- An **always-on device** on your LAN to run the WOL server (NAS, Raspberry Pi, home server, old laptop, etc.)
- Docker already configured
- **Wake-on-LAN enabled in your Gaming PC BIOS** and working

---

# Setup guide

To configure **remWOL-moonlight**, your WOL server must be reachable from anywhere on the internet.

There are two possible approaches:

- Using [**Tailscale VPN**](Tailscale%20guide/README.md)
- Using [**DNS + Port Forwarding**](DNS%20%2B%20port%20forwarding%20guide/README.md) *(recommended)*



---

> [!IMPORTANT]  
> Using **Tailscale** is recommended only if it is already your main way of accessing your gaming PC with Moonlight, or if you have troubles with setting up the DNS.  
> You can still continue using your existing port-forwarded Moonlight setup regardless of whether you choose the DNS method or the Tailscale method.
> By chosing going with Tailscale, youur client device running Moonlight will still need tailscale installed and running

---

> [!WARNING]  
> Installing **Tailscale on SteamOS devices can be somewhat tedious**.  
> This guide will not cover how to install **Tailscale**.  
> Both the **client device and the server must be connected to the same Tailnet** to send WOL requests.

---


