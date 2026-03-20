import requests
import subprocess
import time
import json
import os
import sys
import logging
from datetime import datetime, timedelta

TOKEN   = ""
CHAT_ID = ""
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

HOME    = "/data/data/com.termux/files/home"
LOG_DIR = f"{HOME}/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# ─── Logging setup ────────────────────────────────────────
logging.basicConfig(
    filename=f"{LOG_DIR}/telegram_bot.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger()

BOT_START_TIME = datetime.now()

# ─────────────────────────────────────────
#  CORE HELPERS
# ─────────────────────────────────────────

def send(msg, parse_mode="Markdown", reply_markup=None):
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": parse_mode}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=10)
    except Exception as e:
        log.error(f"send() failed: {e}")

def answer_callback(callback_id, text="✅"):
    try:
        requests.post(f"{BASE_URL}/answerCallbackQuery", json={
            "callback_query_id": callback_id, "text": text
        }, timeout=5)
    except Exception as e:
        log.error(f"answer_callback() failed: {e}")

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
    except:
        return "Error"

def fmt_bytes(b):
    try:
        b = int(b)
        if b < 1024**2:   return f"{b/1024:.1f} KB"
        if b < 1024**3:   return f"{b/1024**2:.1f} MB"
        return f"{b/1024**3:.2f} GB"
    except:
        return "N/A"

def fmt_uptime(seconds):
    td = timedelta(seconds=int(seconds))
    d  = td.days
    h, rem = divmod(td.seconds, 3600)
    m, s   = divmod(rem, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)

# ─────────────────────────────────────────
#  SYSTEM INFO
# ─────────────────────────────────────────

def get_temp():
    try:
        t = run("cat /sys/class/thermal/thermal_zone0/temp")
        return f"{int(t)/1000:.1f}°C"
    except:
        return "N/A"

def get_battery():
    try:
        b = json.loads(run("termux-battery-status"))
        icon   = "🔌" if b.get("status") == "CHARGING" else "🔋"
        health = b.get("health", "?").capitalize()
        plug   = b.get("plugged", "?").replace("_", " ").capitalize()
        return (
            f"{icon} *{b.get('percentage','?')}%* — {b.get('status','?').capitalize()}\n"
            f"   Health: `{health}` | Source: `{plug}`"
        )
    except:
        return "🔋 N/A"

def get_storage():
    try:
        line  = run("df -h /data | tail -1").split()
        return f"💾 `{line[2]}` used / `{line[1]}` total (`{line[4]}` full)"
    except:
        return "💾 N/A"

def get_ram():
    try:
        total = int(run("grep MemTotal /proc/meminfo").split()[1])
        free  = int(run("grep MemAvailable /proc/meminfo").split()[1])
        used  = total - free
        pct   = int(used / total * 100)
        bar   = "█" * (pct // 10) + "░" * (10 - pct // 10)
        return f"🧠 RAM: `{used//1024}MB / {total//1024}MB` ({pct}%)\n   `[{bar}]`"
    except:
        return "🧠 RAM: N/A"

def get_cpu():
    try:
        load = run("cut -d' ' -f1-3 /proc/loadavg")
        cores = run("nproc")
        freq  = run("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq")
        freq_mhz = f"{int(freq)//1000} MHz" if freq != "Error" else "N/A"
        return f"⚡ Load: `{load}` | Cores: `{cores}` | Freq: `{freq_mhz}`"
    except:
        return "⚡ CPU: N/A"

def get_ip():
    local  = run("ip addr show wlan0 | grep 'inet ' | awk '{print $2}'") or "No WiFi"
    public = run("curl -s --max-time 5 ifconfig.me") or "N/A"
    return f"📡 Local:  `{local}`\n🌍 Public: `{public}`"

def get_system_uptime():
    try:
        secs = float(run("awk '{print $1}' /proc/uptime"))
        return f"⏱ System uptime: `{fmt_uptime(secs)}`"
    except:
        return "⏱ Uptime: N/A"

def get_bot_uptime():
    delta = datetime.now() - BOT_START_TIME
    return f"🤖 Bot uptime: `{fmt_uptime(delta.total_seconds())}`"

def get_wifi_signal():
    try:
        sig = run("cat /proc/net/wireless | tail -1 | awk '{print $3}'").replace(".", "")
        return f"📶 WiFi signal: `{sig} dBm`"
    except:
        return "📶 WiFi: N/A"

def jellyfin_status():
    pid = run("pgrep -x jellyfin")
    if pid:
        mem = run(f"ps -p {pid} -o rss= 2>/dev/null")
        mem_mb = f"{int(mem)//1024}MB" if mem and mem != "Error" else "?"
        return f"✅ Running (PID: `{pid}`, RAM: `{mem_mb}`)"
    return "❌ Stopped"

def get_top_processes():
    raw   = run("ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head -9")
    lines = raw.splitlines()
    header = lines[0] if lines else ""
    body   = "\n".join(lines[1:]) if len(lines) > 1 else "N/A"
    return f"```\n{header}\n{body}\n```"

def get_open_ports():
    try:
        out = run("ss -tlnp | grep LISTEN | awk '{print $4}' | sed 's/.*://' | sort -n | uniq")
        return f"🔓 Open ports: `{out.replace(chr(10), ', ')}`"
    except:
        return "🔓 Ports: N/A"

def get_disk_io():
    try:
        line = run("cat /proc/diskstats | grep mmcblk0 | head -1")
        parts = line.split()
        reads, writes = parts[5], parts[9]
        return f"💿 Disk I/O — Reads: `{reads}` sectors | Writes: `{writes}` sectors"
    except:
        return "💿 Disk I/O: N/A"

def get_log_tail(logfile, lines=15):
    try:
        out = run(f"tail -{lines} {logfile}")
        return f"```\n{out[:3500]}\n```" if out else "_(empty)_"
    except:
        return "_(not found)_"

def get_network():
    rx = run("cat /sys/class/net/wlan0/statistics/rx_bytes")
    tx = run("cat /sys/class/net/wlan0/statistics/tx_bytes")
    return (
        f"🌐 *Network — wlan0*\n"
        f"⬇️ Received: `{fmt_bytes(rx)}`\n"
        f"⬆️ Sent:     `{fmt_bytes(tx)}`\n\n"
        f"{get_ip()}\n"
        f"{get_wifi_signal()}"
    )

# ─────────────────────────────────────────
#  JELLYFIN CONTROLS
# ─────────────────────────────────────────

def start_jellyfin():
    if run("pgrep -x jellyfin"):
        return "⚠️ Jellyfin is *already running*."
    run(f"bash {HOME}/jellyfin_service.sh &")
    time.sleep(2)
    return "▶️ Jellyfin *started*!"

def stop_jellyfin():
    if not run("pgrep -x jellyfin"):
        return "⚠️ Jellyfin is *already stopped*."
    run("pkill jellyfin")
    return "⏹ Jellyfin *stopped*."

def restart_jellyfin():
    run("pkill jellyfin")
    time.sleep(1)
    run(f"bash {HOME}/jellyfin_service.sh &")
    time.sleep(2)
    return "🔄 Jellyfin *restarted*."

# ─────────────────────────────────────────
#  FULL STATUS
# ─────────────────────────────────────────

def get_status():
    now = datetime.now().strftime("%d %b %Y  %H:%M:%S")
    return (
        f"📊 *SERVER STATUS*\n"
        f"🕐 {now}\n"
        f"{get_system_uptime()}\n"
        f"{get_bot_uptime()}\n\n"
        f"🎬 Jellyfin: {jellyfin_status()}\n\n"
        f"{get_cpu()}\n"
        f"{get_ram()}\n"
        f"{get_storage()}\n"
        f"🌡 Temp: *{get_temp()}*\n"
        f"{get_battery()}"
    )

# ─────────────────────────────────────────
#  INLINE KEYBOARD
# ─────────────────────────────────────────

MAIN_KEYBOARD = {
    "inline_keyboard": [
        [{"text": "📊 Status",    "callback_data": "status"},
         {"text": "🌐 Network",   "callback_data": "network"}],
        [{"text": "🧠 RAM",       "callback_data": "ram"},
         {"text": "💾 Storage",   "callback_data": "storage"}],
        [{"text": "🌡 Temp",      "callback_data": "temp"},
         {"text": "🔋 Battery",   "callback_data": "battery"}],
        [{"text": "▶️ JF Start",  "callback_data": "jf_start"},
         {"text": "⏹ JF Stop",   "callback_data": "jf_stop"},
         {"text": "🔄 JF Restart","callback_data": "jf_restart"}],
        [{"text": "🔝 Top Procs", "callback_data": "top"},
         {"text": "🔓 Ports",     "callback_data": "ports"}],
        [{"text": "📋 Startup Log","callback_data": "log_startup"},
         {"text": "🤖 Bot Log",   "callback_data": "log_bot"}],
        [{"text": "📡 JF Log",    "callback_data": "log_jf"},
         {"text": "☁️ CF Log",    "callback_data": "log_cf"}],
    ]
}

HELP_TEXT = """\
🤖 *Android Server Bot*

`/status`      — Full system overview
`/uptime`      — System + bot uptime
`/ip`          — Local & public IP
`/network`     — Network stats + WiFi signal
`/temp`        — CPU temperature
`/battery`     — Battery info
`/ram`         — RAM usage
`/storage`     — Storage usage
`/cpu`         — CPU load & frequency
`/top`         — Top processes
`/ports`       — Open listening ports
`/diskio`      — Disk I/O stats
`/jfstart`     — Start Jellyfin
`/jfstop`      — Stop Jellyfin
`/jfrestart`   — Restart Jellyfin
`/jfstatus`    — Jellyfin status
`/logstartup`  — Last 15 lines of startup log
`/logbot`      — Last 15 lines of bot log
`/logjf`       — Last 15 lines of jellyfin log
`/logcf`       — Last 15 lines of cloudflared log
`/menu`        — Show quick-action buttons
`/help`        — This message
"""

# ─────────────────────────────────────────
#  DISPATCHER
# ─────────────────────────────────────────

def handle_message(msg_obj):
    cmd = msg_obj.get("text", "").strip().split()[0].lower().split("@")[0]
    log.info(f"Command received: {cmd}")

    dispatch = {
        "/start":      lambda: send(HELP_TEXT),
        "/help":       lambda: send(HELP_TEXT),
        "/menu":       lambda: send("🎛 *Quick Actions*", reply_markup=MAIN_KEYBOARD),
        "/status":     lambda: send(get_status()),
        "/uptime":     lambda: send(f"{get_system_uptime()}\n{get_bot_uptime()}"),
        "/ip":         lambda: send(get_ip()),
        "/network":    lambda: send(get_network()),
        "/temp":       lambda: send(f"🌡 CPU Temp: *{get_temp()}*"),
        "/battery":    lambda: send(f"🔋 *Battery*\n{get_battery()}"),
        "/ram":        lambda: send(get_ram()),
        "/storage":    lambda: send(get_storage()),
        "/cpu":        lambda: send(get_cpu()),
        "/top":        lambda: send(f"🔝 *Top Processes*\n{get_top_processes()}"),
        "/ports":      lambda: send(get_open_ports()),
        "/diskio":     lambda: send(get_disk_io()),
        "/jfstart":    lambda: send(start_jellyfin()),
        "/jfstop":     lambda: send(stop_jellyfin()),
        "/jfrestart":  lambda: send(restart_jellyfin()),
        "/jfstatus":   lambda: send(f"🎬 Jellyfin: {jellyfin_status()}"),
        "/logstartup": lambda: send(f"📋 *Startup Log*\n{get_log_tail(f'{LOG_DIR}/startup.log')}"),
        "/logbot":     lambda: send(f"🤖 *Bot Log*\n{get_log_tail(f'{LOG_DIR}/telegram_bot.log')}"),
        "/logjf":      lambda: send(f"📡 *Jellyfin Log*\n{get_log_tail(f'{LOG_DIR}/jellyfin_service.log')}"),
        "/logcf":      lambda: send(f"☁️ *Cloudflared Log*\n{get_log_tail(f'{LOG_DIR}/cloudflared.log')}"),
    }

    action = dispatch.get(cmd)
    if action:
        action()
    else:
        send(f"❓ Unknown command: `{cmd}`\nType /help or /menu.")

def handle_callback(cb):
    answer_callback(cb["id"])
    data = cb["data"]
    log.info(f"Callback: {data}")

    cb_dispatch = {
        "status":      lambda: send(get_status()),
        "network":     lambda: send(get_network()),
        "ram":         lambda: send(get_ram()),
        "storage":     lambda: send(get_storage()),
        "temp":        lambda: send(f"🌡 CPU Temp: *{get_temp()}*"),
        "battery":     lambda: send(f"🔋 *Battery*\n{get_battery()}"),
        "jf_start":    lambda: send(start_jellyfin()),
        "jf_stop":     lambda: send(stop_jellyfin()),
        "jf_restart":  lambda: send(restart_jellyfin()),
        "top":         lambda: send(f"🔝 *Top Processes*\n{get_top_processes()}"),
        "ports":       lambda: send(get_open_ports()),
        "log_startup": lambda: send(f"📋 *Startup Log*\n{get_log_tail(f'{LOG_DIR}/startup.log')}"),
        "log_bot":     lambda: send(f"🤖 *Bot Log*\n{get_log_tail(f'{LOG_DIR}/telegram_bot.log')}"),
        "log_jf":      lambda: send(f"📡 *Jellyfin Log*\n{get_log_tail(f'{LOG_DIR}/jellyfin_service.log')}"),
        "log_cf":      lambda: send(f"☁️ *Cloudflared Log*\n{get_log_tail(f'{LOG_DIR}/cloudflared.log')}"),
    }

    action = cb_dispatch.get(data)
    if action:
        action()

# ─────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────

log.info("Bot starting...")
send(
    f"🟢 *Bot is online!*\n"
    f"🕐 {datetime.now().strftime('%d %b %Y %H:%M:%S')}\n"
    f"{get_system_uptime()}\n"
    f"🎬 Jellyfin: {jellyfin_status()}\n\n"
    f"Type /menu for quick actions or /help for all commands.",
    reply_markup=MAIN_KEYBOARD
)
print("Bot started. Polling...")

last_update = None
while True:
    try:
        res = requests.get(f"{BASE_URL}/getUpdates", params={
            "timeout": 60,
            "offset": last_update
        }, timeout=70).json()

        for u in res.get("result", []):
            last_update = u["update_id"] + 1

            if "message" in u:
                if str(u["message"]["chat"]["id"]) == CHAT_ID:
                    handle_message(u["message"])

            if "callback_query" in u:
                if str(u["callback_query"]["message"]["chat"]["id"]) == CHAT_ID:
                    handle_callback(u["callback_query"])

    except Exception as e:
        log.error(f"Loop error: {e}")
        time.sleep(5)
