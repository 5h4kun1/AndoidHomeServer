# 🏠 AndroidHomeServer

Turn your Android phone into a fully automated home media server using Termux — running Jellyfin, SSH, Cloudflare Tunnel, and a Telegram bot for remote control.

---

## 📦 What's Inside

| File | Description |
|------|-------------|
| `scripts/start.sh` | Main boot script — starts all services, watchdog loop, logging |
| `scripts/jellyfin_service.sh` | Jellyfin runner with crash restart + logging |
| `bot/telegram_bot.py` | Telegram bot for remote monitoring & control |
| `docs/SETUP.md` | Full setup guide from scratch |
| `docs/CLOUDFLARE.md` | Cloudflare tunnel setup guide |
| `docs/SCP.md` | File transfer guide (laptop → phone) |

---

## ✨ Features

- 🎬 **Jellyfin** media server — auto-start, auto-restart on crash
- 🔒 **SSH** access for remote terminal
- ☁️ **Cloudflare Tunnel** — expose Jellyfin to internet without port forwarding
- 🤖 **Telegram Bot** — control everything from your phone remotely
- 📋 **Full logging** — all services log to `~/logs/`
- 🐕 **Watchdog** — monitors and restarts dead services every 30s
- 🔁 **Boot persistence** — auto-starts on device reboot via Termux:Boot

---

## 🚀 Quick Start

### 1. Install Termux & packages
```sh
pkg update && pkg upgrade
pkg install openssh tmux nano jellyfin-server python cloudflared
pip install requests
```

### 2. Install Termux:Boot
Download from F-Droid and open it once to enable boot trigger.

### 3. Setup storage & media folders
```sh
termux-setup-storage
mkdir -p ~/storage/shared/JellyFin/Movies
mkdir -p ~/storage/shared/JellyFin/Series
```

### 4. Copy scripts
```sh
mkdir -p ~/.termux/boot
cp scripts/start.sh ~/.termux/boot/start.sh
cp scripts/jellyfin_service.sh ~/jellyfin_service.sh
cp bot/telegram_bot.py ~/telegram_bot.py
chmod +x ~/.termux/boot/start.sh ~/jellyfin_service.sh
```

### 5. Set static IP (recommended)
- Go to your router admin: `http://192.168.1.1`
- Login with `admin` / `admin` (or `multipro` / `multipro` for ZTE)
- Find **DHCP Binding / Address Reservation**
- Add your device MAC + preferred IP (e.g. `192.168.1.69`)

### 6. Reboot your phone
Everything starts automatically. ✅

---

## 📱 Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/status` | Full system overview |
| `/uptime` | System + bot uptime |
| `/ip` | Local & public IP |
| `/network` | Network stats + WiFi signal |
| `/cpu` | CPU load & frequency |
| `/ram` | RAM usage with bar |
| `/temp` | CPU temperature |
| `/battery` | Battery % + health |
| `/storage` | Storage usage |
| `/top` | Top processes |
| `/ports` | Open listening ports |
| `/diskio` | Disk I/O stats |
| `/jfstart` | Start Jellyfin |
| `/jfstop` | Stop Jellyfin |
| `/jfrestart` | Restart Jellyfin |
| `/jfstatus` | Jellyfin status |
| `/logstartup` | Last 15 lines of startup log |
| `/logbot` | Last 15 lines of bot log |
| `/logjf` | Last 15 lines of jellyfin log |
| `/logcf` | Last 15 lines of cloudflared log |
| `/menu` | Inline button keyboard |

---

## 📁 Media Library Paths (inside Jellyfin)
```
/storage/emulated/0/JellyFin/Movies
/storage/emulated/0/JellyFin/Series
```

---

## 📊 Log Files
All logs are stored in `~/logs/`:
```
~/logs/startup.log          ← boot script + watchdog
~/logs/jellyfin_service.log ← jellyfin crashes + restarts
~/logs/telegram_bot.log     ← bot activity + errors
~/logs/cloudflared.log      ← tunnel output
```
Logs auto-rotate when they exceed 5MB.

---

## 🔧 Stability Tips
- Disable battery optimization for **Termux** and **Termux:Boot**
- Enable **Keep WiFi on during sleep** in developer options
- Lock Termux in memory (recent apps → lock)
- Avoid letting the phone overheat

---

## 📡 Remote Access
- **Local:** `http://192.168.1.69:8096`
- **Remote:** `https://luffytheking.dpdns.org` (via Cloudflare Tunnel)
- **SSH:** `ssh -p 8022 u0_a243@192.168.1.69`
