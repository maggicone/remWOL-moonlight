## Step 1  Setup with DuckDNS + Port Forwarding (recommended)

1) Install a DNS service on your server.

In this guide, we will be using [Duck Dns](https://www.duckdns.org/). It's free, but you can use your favourite alternative if you want.

You can follow the official guide here:  
https://www.duckdns.org/install.jsp

There are also many community guides available online to check if you have difficulties installing it.

2) Configure **port forwarding on your router**:

- Port: **8765**
- Protocol: **UDP**
- Destination: **your WOL server IP**

Alternatively, you can choose the port you prefer, but you will need to edit the Docker compose file accordingly in the next step.  
Using port **8765 is recommended**.

Once you are sure that port forwarding and your DNS are correctly configured, you can proceed to setting up the remWOL server in the next step

---------

## Step 2 

