#!/bin/bash
################################################################################
# LOG SESSION END
# Автор: Sandrick Tech
# Описание: Скрипт логирования конца SSH-сессии для systemd unit
# Вызывается: ExecStop в ssh-session@.service
################################################################################

set -euo pipefail

# Получаем SID из параметра
SID="$1"

# Директории
SESSION_DIR="/srv/sys/ssh/ssh_session"
ACTIVE_DIR="$SESSION_DIR/active"
ARCHIVE_DIR="$SESSION_DIR/archive"
METADATA_DIR="$SESSION_DIR/metadata"
MAIN_LOG="/var/log/ssh-sessions.log"

# Создаём директорию архива если не существует
mkdir -p "$ARCHIVE_DIR"

# Текущая дата и время
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
ISO_TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

# Обновляем файл метаданных
METADATA_FILE="$METADATA_DIR/${SID}.metadata"
if [[ -f "$METADATA_FILE" ]]; then
    {
        echo ""
        echo "[END]"
        echo "END_TIME=$TIMESTAMP"
        echo "END_TIME_ISO=$ISO_TIMESTAMP"
        echo "EXIT_CODE=0"
        echo "STATUS=COMPLETED"
    } >> "$METADATA_FILE"
    
    # Вычисляем длительность сессии
    START_TIME=$(grep '^START_TIME=' "$METADATA_FILE" | cut -d'=' -f2)
    START_EPOCH=$(date -d "$START_TIME" +%s 2>/dev/null || echo "0")
    END_EPOCH=$(date +%s)
    DURATION=$((END_EPOCH - START_EPOCH))
    
    echo "DURATION_SECONDS=$DURATION" >> "$METADATA_FILE"
    
    # Форматируем длительность
    HOURS=$((DURATION / 3600))
    MINUTES=$(( (DURATION % 3600) / 60 ))
    SECONDS=$((DURATION % 60))
    echo "DURATION_FORMATTED=${HOURS}h ${MINUTES}m ${SECONDS}s" >> "$METADATA_FILE"
fi

# Обновляем лог сессии
SESSION_LOG="$ACTIVE_DIR/${SID}.log"
if [[ -f "$SESSION_LOG" ]]; then
    {
        echo ""
        echo "[$TIMESTAMP] SESSION ENDED (via systemd)"
        echo "Exit Code: 0"
        echo "Duration: ${HOURS}h ${MINUTES}m ${SECONDS}s"
        echo "═══════════════════════════════════════════════════════════════════"
    } >> "$SESSION_LOG"
    
    # Перемещаем в архив
    mv "$SESSION_LOG" "$ARCHIVE_DIR/"
fi

# Логируем в главный файл
echo "[$TIMESTAMP] SESSION_END | SID=$SID | DURATION=${DURATION}s | METHOD=systemd" >> "$MAIN_LOG"

# Выводим успех
echo "Session ended: $SID (duration: ${HOURS}h ${MINUTES}m ${SECONDS}s)"

exit 0
