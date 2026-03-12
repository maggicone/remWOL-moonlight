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
