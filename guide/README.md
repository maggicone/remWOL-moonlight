# Beginner-Friendly Guide

This guide provides **clear, step-by-step instructions** for anyone setting up **remWOL-Moonlight** from scratch, even with little experience.

**Note**: Some steps link to external software installation guides. If you get stuck, **Google is your friend**.

If you still have issues, feel free to **[open an Issue](https://github.com/maggicone/remWOL-moonlight/issues/new)** describing your problem.

## ⚠️ **IMPORTANT DISCLAIMER**

> [!WARNING]  
> **Most of this project is AI-generated code.**  
> 
> All software in this repository is provided **"AS IS"** — **without warranty of any kind**.  
> 
> The author is **not responsible** for any damage, data loss, or issues caused by following this guide or using the software.

wthout further ado, let's get started

------

# Requirements

- An **always-on device** on your LAN to run the WOL server (NAS, Raspberry Pi, home server, old laptop, etc.)
- **Wake-on-LAN enabled in your PC BIOS** and working

---

# Setup guide

To configure **remWOL-moonlight**, your WOL server must be reachable from anywhere on the internet.

There are two possible approaches:

- Using **Tailscale VPN**
- Using **DuckDNS + Port Forwarding** *(recommended)*

---

> [!IMPORTANT]  
> Using **Tailscale** is recommended only if it is already your main way of accessing your gaming PC with Moonlight.  
> You can still continue using your existing port-forwarded Moonlight setup regardless of whether you choose the DuckDNS method or the Tailscale method.
> By chosing going with Tailscale, youur client device running Moonlight will still need tailscale installed and running

---

> [!WARNING]  
> Installing **Tailscale on SteamOS devices can be somewhat tedious**.  
> This guide will not cover how to install Tailscale.  
> Both the **client device and the server must be connected to the same Tailnet** to send WOL requests.

---

## Method 1 - Setup with DuckDNS + Port Forwarding (recommended)

1) Install DuckDNS on your server.

You can follow the official guide here:  
https://www.duckdns.org/install.jsp

There are also many community guides available online.

2) Configure **port forwarding on your router**:

- Port: **8765**
- Protocol: **UDP**
- Destination: **your WOL server IP**

Alternatively, you can choose the port you prefer, but you will need to edit the Docker compose file accordingly in the next step.  
Using port **8765 is recommended**.

Once you are sure that port forwarding and DuckDNS are correctly configured, you can proceed to [setting up the remWOL server](https://github.com/maggicone/remWOL-moonlight/tree/main/remWOL#setup-guide-for-moonlight)

---

## Method 2 - Setup with Tailscale

1. Install **Tailscale** on your server
2. Install **Tailscale** on your client device
3. Connect both devices to the **same Tailnet**

Once you are sure both devices are connected to the same Tailnet, you can proceed to [setting up the remWOL server](https://github.com/maggicone/remWOL-moonlight/tree/main/remWOL#setup-guide-for-moonlight).
