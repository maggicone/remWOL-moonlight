# Step 1 - Setup DNS service and Port Forwarding

1) Install a **DNS service** on your server.

In this guide, we will be using [Duck Dns](https://www.duckdns.org/). It's free, but you can use your favourite alternative if you want.

You can follow the official guide here to install duckdns:  
https://www.duckdns.org/install.jsp

There are also many community guides available online to check if you have difficulties installing it.

2) Configure **port forwarding on your router**:

- Port: **8765**
- Protocol: **UDP**
- Destination: **your WOL server IP**

Alternatively, you can choose the port you prefer, but you will need to edit the Docker compose file accordingly in the next step.  
Using port **8765 is recommended**.

Once you are sure that port forwarding and your DNS are correctly configured, you can proceed to setting up the remWOL server container in the next step

---------

# Step 2 installing the WOL server container

## Method 1 — Docker CLI

Replace `your-secret-token` with a passord, and  `AA:BB:CC:DD:EE:FF` with your gaming pc MAC address:

```bash
docker run -d \
  --name remwol-moonlight \
  --network host \
  --restart unless-stopped \
  -e WOL_TOKEN=your-secret-token \
  -e 'WOL_DEVICES={"pc":"AA:BB:CC:DD:EE:FF"}' \
  ghcr.io/maggicone/remwol-moonlight:latest
```
---

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

Now switch to your client device that will use Moonlight, and connect it to the internet via **mobile data (4G/5G hotspot)** to ensure you are outside your local network.

From a browser, visit:

```
http://<your-duckdns-domain>:8765
```
A web page should load indicating that the service has been correctly installed and is running. 

>[!IMPORTANT]
>The web page is still a work in progres, you don't need to interact with anything, just make sure it loads.
>Your browser might warn you about security risks, just ignore it and procede. This behavior is expected when dealing with self-hosted services.

If the page does not load, check:

- port forwarding configuration
- DuckDNS setup
- server container is up and running

*Then*

Test Wake-on-LAN by pasting this in the terminal:

```
curl "http://<your-duckdns-domain>:8765/wake/pc?token=your-token"
```

If the PC wakes up, the installation was successfull.
You can now go to the last step: [Moonlight installation](https://github.com/maggicone/remWOL-moonlight/tree/main/moonlight#installation)


