#!/bin/bash
################################################################################
# LOG SESSION START
# Автор: Sandrick Tech
# Описание: Скрипт логирования начала SSH-сессии для systemd unit
# Вызывается: ExecStart в ssh-session@.service
################################################################################

set -euo pipefail

# Получаем SID из параметра
SID="$1"

# Директории
SESSION_DIR="/srv/sys/ssh/ssh_session"
ACTIVE_DIR="$SESSION_DIR/active"
METADATA_DIR="$SESSION_DIR/metadata"
MAIN_LOG="/var/log/ssh-sessions.log"

# Создаём директории если не существуют
mkdir -p "$ACTIVE_DIR"
mkdir -p "$METADATA_DIR"

# Извлекаем компоненты из SID
# Формат: <IP>_<USER>_<DATE>_<TIME>
IFS='_' read -r CLIENT_IP USERNAME DATE_STAMP TIME_STAMP <<< "$SID"

# Текущая дата и время
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
ISO_TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

# Создаём файл метаданных
METADATA_FILE="$METADATA_DIR/${SID}.metadata"
cat > "$METADATA_FILE" <<EOF
# SSH Session Metadata (via systemd)
# Session ID: $SID

[GENERAL]
SID=$SID
START_TIME=$TIMESTAMP
START_TIME_ISO=$ISO_TIMESTAMP
STATUS=ACTIVE
TRACKING_METHOD=systemd

[CLIENT]
IP=$CLIENT_IP

[USER]
USERNAME=$USERNAME
UID=$(id -u "$USERNAME" 2>/dev/null || echo "unknown")
GID=$(id -g "$USERNAME" 2>/dev/null || echo "unknown")

[SERVER]
SERVER_HOSTNAME=$(hostname)
SERVER_IP=$(hostname -I | awk '{print $1}')
EOF

# Создаём файл лога сессии
SESSION_LOG="$ACTIVE_DIR/${SID}.log"
{
    echo "═══════════════════════════════════════════════════════════════════"
    echo "SSH SESSION LOG (SYSTEMD TRACKED)"
    echo "═══════════════════════════════════════════════════════════════════"
    echo "Session ID: $SID"
    echo "Start Time: $TIMESTAMP"
    echo "User: $USERNAME"
    echo "Client IP: $CLIENT_IP"
    echo "Server: $(hostname)"
    echo "Systemd Unit: ssh-session@${SID}.service"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "[$TIMESTAMP] SESSION STARTED (via systemd)"
} > "$SESSION_LOG"

# Логируем в главный файл
echo "[$TIMESTAMP] SESSION_START | SID=$SID | USER=$USERNAME | IP=$CLIENT_IP | METHOD=systemd" >> "$MAIN_LOG"

# Выводим успех
echo "Session started: $SID"

exit 0
