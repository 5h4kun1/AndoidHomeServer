# ☁️ Cloudflare Tunnel Setup

Expose your Jellyfin server to the internet without port forwarding using Cloudflare Tunnel.

---

## Prerequisites
- A Cloudflare account (free)
- A domain added to Cloudflare (or use a free `*.dpdns.org` subdomain)

---

## Step 1 — Install cloudflared
```sh
pkg install cloudflared
```

---

## Step 2 — Login to Cloudflare
```sh
cloudflared tunnel login
```
This opens a browser link — open it on any device and authorize.

---

## Step 3 — Create the Tunnel
```sh
cloudflared tunnel create jellyfin
```
Note the tunnel ID printed in the output.

---

## Step 4 — Configure the Tunnel
```sh
mkdir -p ~/.cloudflared
nano ~/.cloudflared/config.yml
```

Paste this (replace `YOUR_TUNNEL_ID`):
```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /data/data/com.termux/files/home/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: luffytheking.dpdns.org
    service: http://localhost:8096
  - service: http_status:404
```

---

## Step 5 — Route DNS
```sh
cloudflared tunnel route dns jellyfin luffytheking.dpdns.org
```
This only needs to be done once (the boot script runs it every time just in case).

---

## Step 6 — Test it
```sh
cloudflared tunnel run jellyfin
```
Then open `https://luffytheking.dpdns.org` in a browser.

---

## Step 7 — Let start.sh handle it
The `start.sh` boot script automatically:
1. Runs `cloudflared tunnel route dns` on every boot
2. Starts `cloudflared tunnel run jellyfin` in a tmux session
3. Restarts it via watchdog if it crashes
