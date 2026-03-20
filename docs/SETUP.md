# 📖 Full Setup Guide

## Step 1 — Install Termux
Download Termux from **F-Droid** (not Play Store — Play Store version is outdated).
- F-Droid: https://f-droid.org/packages/com.termux/
- Also install **Termux:Boot** from F-Droid

---

## Step 2 — Update & Install Packages
```sh
pkg update && pkg upgrade
pkg install openssh tmux nano jellyfin-server python cloudflared
pip install requests
```

---

## Step 3 — Setup Storage
```sh
termux-setup-storage
mkdir -p ~/storage/shared/JellyFin/Movies
mkdir -p ~/storage/shared/JellyFin/Series
```

---

## Step 4 — SSH Setup
```sh
# Start SSH
sshd

# Set a password for SSH login
passwd

# Your SSH username (note yours down)
whoami
```
Connect from laptop:
```sh
ssh -p 8022 YOUR_USERNAME@192.168.1.69
```

---

## Step 5 — Deploy Scripts
```sh
# Boot script
mkdir -p ~/.termux/boot
cp start.sh ~/.termux/boot/start.sh
chmod +x ~/.termux/boot/start.sh

# Jellyfin service
cp jellyfin_service.sh ~/jellyfin_service.sh
chmod +x ~/jellyfin_service.sh

# Telegram bot
cp telegram_bot.py ~/telegram_bot.py
```

---

## Step 6 — Static IP on Router
1. Open `http://192.168.1.1` in browser
2. Login (`admin`/`admin` or `multipro`/`multipro` for ZTE F670L)
3. Go to **Network → LAN → DHCP Binding**
4. Add:
   - MAC: your device MAC (disable MAC randomization in WiFi settings first)
   - IP: `192.168.1.69` (or your choice in `192.168.1.2–254`)
   - Name: `android-server`

To find your device MAC:
```sh
# In Termux
ip link show wlan0 | grep ether
```

---

## Step 7 — Open Termux:Boot
Just open the Termux:Boot app once — this registers the boot trigger. Then reboot your phone.

---

## Step 8 — Access Jellyfin
Open in browser: `http://192.168.1.69:8096`

On first run, follow the setup wizard and add libraries:
- Movies: `/storage/emulated/0/JellyFin/Movies`
- Series: `/storage/emulated/0/JellyFin/Series`

---

## Step 9 — Stability Settings
- **Settings → Apps → Termux → Battery → Unrestricted**
- **Settings → Apps → Termux:Boot → Battery → Unrestricted**
- **Developer Options → Keep WiFi on during sleep → Always**
- Lock Termux in recent apps menu
