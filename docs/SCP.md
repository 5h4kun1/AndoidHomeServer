# 📤 File Transfer — Laptop to Phone

Transfer movies and series directly from your laptop to the phone over WiFi using SCP.

---

## Basic Syntax
```sh
scp -P 8022 SOURCE USERNAME@PHONE_IP:DESTINATION
```

---

## Examples

### Single movie
```sh
scp -P 8022 "Inception.mkv" u0_a243@192.168.1.69:/storage/emulated/0/JellyFin/Movies/
```

### Entire Movies folder
```sh
scp -r -P 8022 Movies/ u0_a243@192.168.1.69:/storage/emulated/0/JellyFin/Movies/
```

### TV Series folder
```sh
scp -r -P 8022 "Breaking Bad/" u0_a243@192.168.1.69:/storage/emulated/0/JellyFin/Series/
```

---

## Find Your SSH Username
```sh
# Run in Termux
whoami
```

---

## Tips
- Make sure SSH is running on the phone (`sshd` in Termux)
- Both devices must be on the same WiFi network
- Phone IP is `192.168.1.69` (static, as configured)
- For large transfers, use `rsync` instead for resume support:

```sh
rsync -avz --progress -e "ssh -p 8022" Movies/ u0_a243@192.168.1.69:/storage/emulated/0/JellyFin/Movies/
```
