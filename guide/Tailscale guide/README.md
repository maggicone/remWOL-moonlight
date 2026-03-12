# Step 1 - Setup Tailscale

1) Install **Tailscale** on your server and on your client device (the device that will run Moonlight).

Download Tailscale here:
[https://tailscale.com/download](https://tailscale.com/download)

There are also many community guides available online if you have difficulties installing it.

2) Connect **both devices to the same Tailnet** by logging in with the same Tailscale account on both.

Once both devices appear as connected in your Tailscale dashboard, you can proceed to setting up the remWOL server container in the next step.

---

# Step 2 — Installing the WOL Server Container

Replace `your-secret-token` with a secret password, and `AA:BB:CC:DD:EE:FF` with your gaming PC MAC address:

## Method 1 — Docker CLI

```bash
docker run -d \
  --name remwol-moonlight \
  --network host \
  --restart unless-stopped \
  -e WOL_TOKEN=your-secret-token \
  -e 'WOL_DEVICES={"pc":"AA:BB:CC:DD:EE:FF"}' \
  ghcr.io/maggicone/remwol-moonlight:latest

```

## Method 2 — Stack (Portainer)

Go to **Stacks** → **Add stack**, paste the following and replace your values:

```yaml
services:
  remwol-moonlight:
    image: ghcr.io/maggicone/remwol-moonlight:latest
    container_name: remwol-moonlight
    restart: unless-stopped
    network_mode: host
    environment:
      - WOL_TOKEN=your-secret-token
      - WOL_DEVICES={"pc":"AA:BB:CC:DD:EE:FF"}
      - PYTHONUNBUFFERED=1
```

Click **Deploy the stack**.

## Check Everything Is Working

Now switch to your client device that will use Moonlight, and reconnect it to Tailscale to ensure the tunnel is active.

From a browser, visit:

```
http://<your-tailscale-server-ip>:8765
```

You can find your server's Tailscale IP in the [Tailscale dashboard](https://login.tailscale.com/admin/machines) — it looks like `100.x.x.x`.

A web page should load indicating that the service is correctly installed and running.

> [!IMPORTANT]
> The web page is still a work in progress, you don't need to interact with anything, just make sure it loads.
> Your browser might warn you about security risks, just ignore it and proceed. This behavior is expected when dealing with self-hosted services.

If the page does not load, check:

- Both devices are connected to the same Tailnet
- The server container is up and running

Then test Wake-on-LAN by pasting this in the terminal:

```
curl "http://<your-tailscale-server-ip>:8765/wake/pc?token=your-token"
```

If the PC wakes up, the installation was successful.
You can now go to the last step.

---

# Step 3 — Setup Moonlight

If you made it this far, your server is up and running and is able to wake your PC over the network. **remWOL-Moonlight** is the bridge that lets Moonlight trigger that process directly from the app itself.

> [!WARNING]
> On Windows, uninstall any existing version of Moonlight before proceeding.

### Installation

Download and install the patched version of Moonlight for your OS from the [Releases](https://github.com/maggicone/remWOL-moonlight/releases/) page.

### Configuration

Open Moonlight, go to **Settings** and scroll down to the **Wake-on-LAN** section.

1. Tick **Enable Wake-on-LAN**
2. Fill in the two fields:

| Field | Value |
|---|---|
| **API URL** | `http://<your-tailscale-server-ip>:8765/wake/pc` |
| **Auth Token** | your secret token |

### Usage

When you click on a paired PC that is offline, a new **Wake PC (API)** button will appear. Click it to send the wake request to your server.

Enjoy.
