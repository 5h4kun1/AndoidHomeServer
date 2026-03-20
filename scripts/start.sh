#!/data/data/com.termux/files/usr/bin/sh

# ─── Paths ────────────────────────────────────────────────
HOME=/data/data/com.termux/files/home
BIN=/data/data/com.termux/files/usr/bin
LOG_DIR=$HOME/logs
MAIN_LOG=$LOG_DIR/startup.log
BOT_LOG=$LOG_DIR/telegram_bot.log
CF_LOG=$LOG_DIR/cloudflared.log

mkdir -p "$LOG_DIR"

export PATH=$BIN:$PATH
export DOTNET_ROOT=/data/data/com.termux/files/usr/lib/dotnet

# ─── Logger ───────────────────────────────────────────────
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$MAIN_LOG"
}

# ─── Rotate logs > 5MB ────────────────────────────────────
rotate_log() {
  [ -f "$1" ] && [ $(wc -c < "$1") -gt 5242880 ] && mv "$1" "$1.old" && log "Rotated $1"
}

rotate_log "$MAIN_LOG"
rotate_log "$BOT_LOG"
rotate_log "$CF_LOG"

# ─── Internet check ───────────────────────────────────────
wait_for_internet() {
  log "Waiting for internet..."
  while ! ping -c 1 -W 2 8.8.8.8 > /dev/null 2>&1; do
    sleep 5
  done
  log "Internet is up."
}

# ─── Service starters ─────────────────────────────────────
start_sshd() {
  if ! pgrep -x sshd > /dev/null; then
    $BIN/sshd && log "SSH started." || log "SSH failed to start."
  fi
}

start_jellyfin() {
  if ! tmux has-session -t jellyfin 2>/dev/null; then
    tmux new-session -d -s jellyfin "$HOME/jellyfin_service.sh" && \
      log "Jellyfin session started." || log "Jellyfin failed to start."
  fi
}

start_cloudflared() {
  if ! tmux has-session -t cloudflared 2>/dev/null; then
    tmux new-session -d -s cloudflared \
      "cloudflared tunnel run jellyfin 2>&1 | tee -a $CF_LOG" && \
      log "Cloudflared tunnel started." || log "Cloudflared failed to start."
  fi
}

start_telegram_bot() {
  if ! pgrep -f telegram_bot.py > /dev/null; then
    python $HOME/telegram_bot.py >> "$BOT_LOG" 2>&1 &
    log "Telegram bot started (PID $!)."
  fi
}

# ─── Boot sequence ────────────────────────────────────────
log "════════ BOOT SEQUENCE STARTED ════════"
sleep 40
log "Initial sleep done."

termux-wake-lock
log "Wake lock acquired."

start_sshd
start_jellyfin

wait_for_internet

log "Registering Cloudflare DNS route..."
cloudflared tunnel route dns jellyfin luffytheking.dpdns.org >> "$MAIN_LOG" 2>&1

start_cloudflared
start_telegram_bot

log "════════ BOOT SEQUENCE COMPLETE ════════"

# ─── Watchdog loop ────────────────────────────────────────
CYCLE=0
while true; do
  sleep 30
  CYCLE=$((CYCLE + 1))

  # Always check these
  start_sshd
  start_jellyfin

  # Check network-dependent services only when online
  if ping -c 1 -W 2 8.8.8.8 > /dev/null 2>&1; then
    start_cloudflared
    start_telegram_bot
  else
    log "Internet down — skipping cloudflared & bot check."
  fi

  # Rotate logs every 100 cycles (~50 min)
  if [ $((CYCLE % 100)) -eq 0 ]; then
    rotate_log "$MAIN_LOG"
    rotate_log "$BOT_LOG"
    rotate_log "$CF_LOG"
  fi

done
