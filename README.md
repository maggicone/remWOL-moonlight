# What is remWOL-moonlight?

remWOL-moonlight is a project that integrates Directly into Moonlight a new button to remotely wake your pc anywhere in the world, with or without the need of a VPN, such as Tailscale.

<img width="450" height="450" alt="image" src="https://github.com/user-attachments/assets/bffa5ce5-0494-4876-9877-ee53661f3fdd" /> <img width="450" height="450" alt="image2" src="https://github.com/user-attachments/assets/002c5f83-16ba-4539-92fc-b4d08a68b50a" />



## How doese it work?

This project uses a slightly custom version of moonlight with an added **Wake PC (API)** button that calls the WOL server directly from the Moonlight interface


1. You click **Wake PC (API)** in the Moonlight fork
2. Moonlight calls `GET /wake/<device>?token=<your-token>` on the WOL server
3. The server sends a UDP magic packet on the local network
4. Your PC powers on
5. Moonlight connects and starts streaming

<img width="700" height="922" alt="immagine" src="https://github.com/user-attachments/assets/4cdee816-ab51-4526-948b-9ff166bbdc7c" />

```
Moonlight fork  ──→  WOL API Server  ──→  Magic Packet  ──→  Your PC wakes up
  (client)             (self-hosted)         (UDP broadcast)
```




## Requirements

- An always-on device on your LAN to run the WOL server (NAS, Raspberry Pi, home server)
- Wake-on-LAN enabled in your PC's BIOS and working
- Moonlight fork installed on your streaming device — **Linux only (AppImage)** for now


# Setup guide

To configure remWOL-moonlight you need to be able to reach your server from all over the world. you have 2 routs: using **Tailscale VPN** (Or the VPN you prefer) or **Duckdns + port forwarding** (reccomanded)

>[!IMPORTANT]
>L' utilizzo di tailscale è consigliato se Tailscale è già il tuo unico modo per raggiungere il tuo PC da gioco con moonlight. Puoi comunque continuare ad accedere al tuo PC da gioco tramite port forwarding se decidi di usare questo modo.

> [!WARNING]
> Tailscale can be a bit tedious to install on steamos devices. I will not cover how to install Tailscale on this guide. The client device and the server will need to be connected to your tailnet to be able to sent WOL requests.

## Setup with Duckdns + port forwarding

[install Duckdns](https://www.duckdns.org/install.jsp) on your server. There is also a lot of guides online on how to do it. 

Then you want to port forward the ports 8765 udp/utc of your server.



## Setup with Tailscale

Install Tailscale on both your server and your client and connect them to the same Tailnet.

---------
porzione scritta da chat gpt:



# What is remWOL-moonlight?

**remWOL-moonlight** is a project that integrates a new button directly into Moonlight that allows you to **wake your PC remotely from anywhere in the world**, with or without a VPN such as Tailscale.

<img width="450" height="450" alt="image" src="https://github.com/user-attachments/assets/bffa5ce5-0494-4876-9877-ee53661f3fdd" />
<img width="450" height="450" alt="image2" src="https://github.com/user-attachments/assets/002c5f83-16ba-4539-92fc-b4d08a68b50a" />

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

<img width="700" height="922" alt="immagine" src="https://github.com/user-attachments/assets/4cdee816-ab51-4526-948b-9ff166bbdc7c" />


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
> If you choose the DuckDNS + port forwarding method, you can continue using your existing port-forwarded Moonlight setup.

---

> [!WARNING]  
> Installing **Tailscale on SteamOS devices can be somewhat tedious**.  
> This guide will not cover how to install Tailscale.  
> Both the **client device and the server must be connected to the same Tailnet** to send WOL requests.

---

# Setup with DuckDNS + Port Forwarding

1) Install DuckDNS on your server.

You can follow the official guide here:  
https://www.duckdns.org/install.jsp

There are also many community guides available online.

2) configure **port forwarding on your router**:

- Port: **8765**
- Protocol: **UDP**
- Destination: **your WOL server IP**

Alternatively, you can chose the port you prefer, but you will need to edit the compose file of the docker file accordingly.
---

# Setup with Tailscale

1. Install **Tailscale** on your server
2. Install **Tailscale** on your client device
3. Connect both devices to the **same Tailnet**

Once connected, Moonlight will be able to send WOL requests through the Tailscale network.
-----------------

