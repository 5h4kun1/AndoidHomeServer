#!/data/data/com.termux/files/usr/bin/sh

export PATH=/data/data/com.termux/files/usr/bin:$PATH
export DOTNET_ROOT=/data/data/com.termux/files/usr/lib/dotnet

LOG=/data/data/com.termux/files/home/logs/jellyfin_service.log

mkdir -p "$(dirname $LOG)"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG"
}

RESTARTS=0

while true; do
  log "Starting Jellyfin... (restart #$RESTARTS)"
  /data/data/com.termux/files/usr/bin/jellyfin >> "$LOG" 2>&1
  EXIT_CODE=$?
  RESTARTS=$((RESTARTS + 1))
  log "Jellyfin stopped (exit code: $EXIT_CODE). Restart #$RESTARTS in 5s..."
  sleep 5
done
