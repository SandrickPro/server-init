#!/bin/bash
################################################################################
# SSH SID SYSTEM v1.0
# Автор: Sandrick Tech
# Дата: 2024-12-08
# Описание: Система Session ID для аудита SSH-сессий согласно ТЗ histor.txt
#
# Основной функционал:
#   - Генерация уникального SID: <IP>_<USER>_<DATE>_<STARTTIME>
#   - Логирование начала и конца каждой SSH-сессии
#   - Создание файлов сессий в /srv/sys/ssh/ssh_session/
#   - Интеграция с PAM для автоматического запуска
#   - Отслеживание команд и активности в рамках сессии
#
# Структура SID:
#   192.168.1.100_john_20241208_143052
#      └── IP: 192.168.1.100
#      └── USER: john
#      └── DATE: 20241208 (YYYYMMDD)
#      └── STARTTIME: 143052 (HHMMSS)
#
# Логи хранятся:
#   /srv/sys/ssh/ssh_session/<SID>.log
#   /srv/sys/ssh/ssh_session/<SID>.metadata
################################################################################

# Строгий режим выполнения
set -euo pipefail

################################################################################
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
################################################################################

# Базовая директория для SSH сессий
SESSION_DIR="/srv/sys/ssh/ssh_session"

# Директория для метаданных
METADATA_DIR="$SESSION_DIR/metadata"

# Директория для активных сессий
ACTIVE_DIR="$SESSION_DIR/active"

# Директория для архива завершённых сессий
ARCHIVE_DIR="$SESSION_DIR/archive"

# Главный лог-файл всех сессий
MAIN_LOG="/var/log/ssh-sessions.log"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

################################################################################
# УТИЛИТЫ
################################################################################

###
# Функция: log_to_main
# Описание: Логирование в главный файл
# Параметры:
#   $1 - сообщение
###
log_to_main() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" >> "$MAIN_LOG"
}

################################################################################
# ИНИЦИАЛИЗАЦИЯ
################################################################################

###
# Функция: init_directories
# Описание: Создание структуры директорий для SID системы
###
init_directories() {
    mkdir -p "$SESSION_DIR"
    mkdir -p "$METADATA_DIR"
    mkdir -p "$ACTIVE_DIR"
    mkdir -p "$ARCHIVE_DIR"
    
    # Устанавливаем права (только root может читать/писать)
    chmod 700 "$SESSION_DIR"
    chmod 700 "$METADATA_DIR"
    chmod 700 "$ACTIVE_DIR"
    chmod 700 "$ARCHIVE_DIR"
}

################################################################################
# ГЕНЕРАЦИЯ SID
################################################################################

###
# Функция: generate_sid
# Описание: Генерация уникального Session ID
# Параметры:
#   $1 - IP адрес клиента
#   $2 - имя пользователя
# Возвращает: SID в формате <IP>_<USER>_<DATE>_<STARTTIME>
###
generate_sid() {
    local client_ip="$1"
    local username="$2"
    
    # Получаем текущую дату и время
    local date_stamp=$(date '+%Y%m%d')
    local time_stamp=$(date '+%H%M%S')
    
    # Очищаем IP от двоеточий (для IPv6)
    local clean_ip="${client_ip//:/_}"
    
    # Формируем SID
    local sid="${clean_ip}_${username}_${date_stamp}_${time_stamp}"
    
    echo "$sid"
}

################################################################################
# ЛОГИРОВАНИЕ НАЧАЛА СЕССИИ
################################################################################

###
# Функция: log_session_start
# Описание: Логирование начала SSH-сессии
# Параметры:
#   $1 - SID
#   $2 - IP адрес клиента
#   $3 - имя пользователя
#   $4 - порт SSH
###
log_session_start() {
    local sid="$1"
    local client_ip="$2"
    local username="$3"
    local ssh_port="${4:-22}"
    
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local iso_timestamp=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
    
    # Создаём файл метаданных сессии
    local metadata_file="$METADATA_DIR/${sid}.metadata"
    cat > "$metadata_file" <<EOF
# SSH Session Metadata
# Session ID: $sid

[GENERAL]
SID=$sid
START_TIME=$timestamp
START_TIME_ISO=$iso_timestamp
STATUS=ACTIVE

[CLIENT]
IP=$client_ip
HOSTNAME=$(host "$client_ip" 2>/dev/null | awk '{print $NF}' || echo "unknown")

[USER]
USERNAME=$username
UID=$(id -u "$username" 2>/dev/null || echo "unknown")
GID=$(id -g "$username" 2>/dev/null || echo "unknown")
GROUPS=$(id -Gn "$username" 2>/dev/null || echo "unknown")
HOME=$(getent passwd "$username" | cut -d: -f6)
SHELL=$(getent passwd "$username" | cut -d: -f7)

[SERVER]
SSH_PORT=$ssh_port
SERVER_HOSTNAME=$(hostname)
SERVER_IP=$(hostname -I | awk '{print $1}')

[ENVIRONMENT]
SSH_CONNECTION=${SSH_CONNECTION:-"N/A"}
SSH_CLIENT=${SSH_CLIENT:-"N/A"}
SSH_TTY=${SSH_TTY:-"N/A"}
TERM=${TERM:-"N/A"}
EOF
    
    # Создаём файл лога сессии
    local session_log="$ACTIVE_DIR/${sid}.log"
    {
        echo "═══════════════════════════════════════════════════════════════════"
        echo "SSH SESSION LOG"
        echo "═══════════════════════════════════════════════════════════════════"
        echo "Session ID: $sid"
        echo "Start Time: $timestamp"
        echo "User: $username"
        echo "Client IP: $client_ip"
        echo "Server: $(hostname)"
        echo "═══════════════════════════════════════════════════════════════════"
        echo ""
        echo "[$timestamp] SESSION STARTED"
    } > "$session_log"
    
    # Логируем в главный файл
    log_to_main "SESSION_START | SID=$sid | USER=$username | IP=$client_ip"
    
    # Создаём символическую ссылку на активную сессию пользователя
    ln -sf "$session_log" "$ACTIVE_DIR/current_${username}_${client_ip}"
    
    echo "$sid"
}

################################################################################
# ЛОГИРОВАНИЕ КОНЦА СЕССИИ
################################################################################

###
# Функция: log_session_end
# Описание: Логирование конца SSH-сессии
# Параметры:
#   $1 - SID
#   $2 - exit code (необязательно)
###
log_session_end() {
    local sid="$1"
    local exit_code="${2:-0}"
    
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local iso_timestamp=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
    
    # Обновляем файл метаданных
    local metadata_file="$METADATA_DIR/${sid}.metadata"
    if [[ -f "$metadata_file" ]]; then
        {
            echo ""
            echo "[END]"
            echo "END_TIME=$timestamp"
            echo "END_TIME_ISO=$iso_timestamp"
            echo "EXIT_CODE=$exit_code"
            echo "STATUS=COMPLETED"
        } >> "$metadata_file"
        
        # Вычисляем длительность сессии
        local start_time=$(grep '^START_TIME=' "$metadata_file" | cut -d'=' -f2)
        local start_epoch=$(date -d "$start_time" +%s 2>/dev/null || echo "0")
        local end_epoch=$(date +%s)
        local duration=$((end_epoch - start_epoch))
        
        echo "DURATION_SECONDS=$duration" >> "$metadata_file"
        
        # Форматируем длительность в человекочитаемый вид
        local hours=$((duration / 3600))
        local minutes=$(( (duration % 3600) / 60 ))
        local seconds=$((duration % 60))
        echo "DURATION_FORMATTED=${hours}h ${minutes}m ${seconds}s" >> "$metadata_file"
    fi
    
    # Обновляем лог сессии
    local session_log="$ACTIVE_DIR/${sid}.log"
    if [[ -f "$session_log" ]]; then
        {
            echo ""
            echo "[$timestamp] SESSION ENDED"
            echo "Exit Code: $exit_code"
            echo "═══════════════════════════════════════════════════════════════════"
        } >> "$session_log"
        
        # Перемещаем в архив
        mv "$session_log" "$ARCHIVE_DIR/"
        
        # Удаляем символическую ссылку
        local username=$(grep '^USERNAME=' "$metadata_file" | cut -d'=' -f2)
        local client_ip=$(grep '^IP=' "$metadata_file" | cut -d'=' -f2)
        rm -f "$ACTIVE_DIR/current_${username}_${client_ip}"
    fi
    
    # Логируем в главный файл
    log_to_main "SESSION_END | SID=$sid | EXIT_CODE=$exit_code | DURATION=${duration}s"
}

################################################################################
# ЛОГИРОВАНИЕ АКТИВНОСТИ В СЕССИИ
################################################################################

###
# Функция: log_session_activity
# Описание: Логирование активности внутри сессии
# Параметры:
#   $1 - SID
#   $2 - тип события (COMMAND, LOGIN, LOGOUT, ERROR и т.д.)
#   $3 - сообщение
###
log_session_activity() {
    local sid="$1"
    local event_type="$2"
    local message="$3"
    
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local session_log="$ACTIVE_DIR/${sid}.log"
    
    if [[ -f "$session_log" ]]; then
        echo "[$timestamp] [$event_type] $message" >> "$session_log"
    fi
}

################################################################################
# ПОЛУЧЕНИЕ ИНФОРМАЦИИ О СЕССИИ
################################################################################

###
# Функция: get_current_sid
# Описание: Получить SID текущей SSH-сессии
# Возвращает: SID или пустую строку
###
get_current_sid() {
    # Извлекаем IP клиента из переменной окружения SSH_CONNECTION
    if [[ -n "${SSH_CONNECTION:-}" ]]; then
        local client_ip=$(echo "$SSH_CONNECTION" | awk '{print $1}')
        local username="$USER"
        
        # Ищем активную сессию для этого пользователя и IP
        local link_file="$ACTIVE_DIR/current_${username}_${client_ip}"
        if [[ -L "$link_file" ]]; then
            local log_file=$(readlink "$link_file")
            local sid=$(basename "$log_file" .log)
            echo "$sid"
            return 0
        fi
    fi
    
    echo ""
}

###
# Функция: list_active_sessions
# Описание: Показать все активные сессии
###
list_active_sessions() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}          АКТИВНЫЕ SSH-СЕССИИ                               ${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    local count=0
    for log_file in "$ACTIVE_DIR"/*.log; do
        [[ ! -f "$log_file" ]] && continue
        
        local sid=$(basename "$log_file" .log)
        local metadata_file="$METADATA_DIR/${sid}.metadata"
        
        if [[ -f "$metadata_file" ]]; then
            local username=$(grep '^USERNAME=' "$metadata_file" | cut -d'=' -f2)
            local client_ip=$(grep '^IP=' "$metadata_file" | cut -d'=' -f2)
            local start_time=$(grep '^START_TIME=' "$metadata_file" | cut -d'=' -f2)
            
            # Вычисляем длительность
            local start_epoch=$(date -d "$start_time" +%s 2>/dev/null || echo "0")
            local current_epoch=$(date +%s)
            local duration=$((current_epoch - start_epoch))
            local hours=$((duration / 3600))
            local minutes=$(( (duration % 3600) / 60 ))
            
            echo -e "${GREEN}[ACTIVE]${NC} $sid"
            echo "  User: $username"
            echo "  IP: $client_ip"
            echo "  Started: $start_time"
            echo "  Duration: ${hours}h ${minutes}m"
            echo ""
            
            ((count++))
        fi
    done
    
    if [[ $count -eq 0 ]]; then
        echo -e "${YELLOW}Нет активных сессий${NC}"
    else
        echo -e "${GREEN}Всего активных сессий: $count${NC}"
    fi
}

###
# Функция: show_session_details
# Описание: Показать детали конкретной сессии
# Параметры:
#   $1 - SID
###
show_session_details() {
    local sid="$1"
    
    local metadata_file="$METADATA_DIR/${sid}.metadata"
    local log_file="$ACTIVE_DIR/${sid}.log"
    
    # Проверяем, если сессия завершена
    if [[ ! -f "$log_file" ]]; then
        log_file="$ARCHIVE_DIR/${sid}.log"
    fi
    
    if [[ ! -f "$metadata_file" ]]; then
        echo -e "${RED}Сессия $sid не найдена${NC}"
        return 1
    fi
    
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}          ДЕТАЛИ СЕССИИ: $sid                               ${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Выводим метаданные
    cat "$metadata_file"
    
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}          ЛОГ СЕССИИ                                         ${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Выводим последние 50 строк лога
    if [[ -f "$log_file" ]]; then
        tail -n 50 "$log_file"
    else
        echo -e "${YELLOW}Лог сессии не найден${NC}"
    fi
}

################################################################################
# ИНТЕГРАЦИЯ С PAM
################################################################################

###
# Функция: install_pam_hooks
# Описание: Установка PAM хуков для автоматического логирования сессий
###
install_pam_hooks() {
    echo -e "${CYAN}Установка PAM хуков для SSH SID системы...${NC}"
    
    # Создаём скрипт для логирования входа
    local pam_login_script="/usr/local/bin/ssh-sid-login.sh"
    cat > "$pam_login_script" <<'EOF'
#!/bin/bash
# Автоматическое логирование начала SSH-сессии

# Получаем информацию о подключении
CLIENT_IP=$(echo "$PAM_RHOST" | awk '{print $1}')
USERNAME="$PAM_USER"
SSH_PORT="22"

# Источник функций SID системы
source /srv/sys/ssh/ssh-sid-system.sh

# Инициализируем директории
init_directories

# Генерируем SID
SID=$(generate_sid "$CLIENT_IP" "$USERNAME")

# Логируем начало сессии
log_session_start "$SID" "$CLIENT_IP" "$USERNAME" "$SSH_PORT"

# Сохраняем SID в переменную окружения для текущей сессии
echo "export SSH_SID=$SID" >> "$HOME/.ssh_session_env"

exit 0
EOF
    
    # Создаём скрипт для логирования выхода
    local pam_logout_script="/usr/local/bin/ssh-sid-logout.sh"
    cat > "$pam_logout_script" <<'EOF'
#!/bin/bash
# Автоматическое логирование конца SSH-сессии

# Получаем SID из переменной окружения
if [[ -f "$HOME/.ssh_session_env" ]]; then
    source "$HOME/.ssh_session_env"
    
    # Источник функций SID системы
    source /srv/sys/ssh/ssh-sid-system.sh
    
    # Логируем конец сессии
    if [[ -n "$SSH_SID" ]]; then
        log_session_end "$SSH_SID" "${PAM_EXIT_CODE:-0}"
    fi
    
    # Удаляем временный файл
    rm -f "$HOME/.ssh_session_env"
fi

exit 0
EOF
    
    # Устанавливаем права на выполнение
    chmod 755 "$pam_login_script"
    chmod 755 "$pam_logout_script"
    
    # Копируем основной скрипт в системную директорию
    cp "$0" /srv/sys/ssh/ssh-sid-system.sh
    chmod 755 /srv/sys/ssh/ssh-sid-system.sh
    
    # Добавляем строки в /etc/pam.d/sshd
    local pam_config="/etc/pam.d/sshd"
    
    # Проверяем, не установлены ли уже хуки
    if grep -q "ssh-sid-login.sh" "$pam_config"; then
        echo -e "${YELLOW}PAM хуки уже установлены${NC}"
    else
        echo -e "${GREEN}Добавление PAM хуков в $pam_config...${NC}"
        
        # Резервная копия
        cp "$pam_config" "${pam_config}.backup_$(date +%Y%m%d_%H%M%S)"
        
        # Добавляем хуки
        {
            echo ""
            echo "# SSH SID System - автоматическое логирование сессий"
            echo "session optional pam_exec.so $pam_login_script"
            echo "session optional pam_exec.so seteuid $pam_logout_script"
        } >> "$pam_config"
        
        echo -e "${GREEN}PAM хуки установлены успешно${NC}"
    fi
}

################################################################################
# CLI ИНТЕРФЕЙС
################################################################################

###
# Функция: usage
# Описание: Вывод справки по использованию
###
usage() {
    cat <<EOF
SSH SID System v1.0 - Система Session ID для аудита SSH-сессий

Использование:
  $0 <команда> [параметры]

Команды:
  init              - Инициализация структуры директорий
  start <user> <ip> - Начать новую сессию (возвращает SID)
  end <sid>         - Завершить сессию
  list              - Показать все активные сессии
  show <sid>        - Показать детали сессии
  current           - Показать SID текущей сессии
  install-pam       - Установить PAM хуки для автоматического логирования
  help              - Показать эту справку

Примеры:
  $0 init
  $0 start john 192.168.1.100
  $0 end 192.168.1.100_john_20241208_143052
  $0 list
  $0 show 192.168.1.100_john_20241208_143052
  $0 current
  $0 install-pam

EOF
}

################################################################################
# ГЛАВНАЯ ФУНКЦИЯ
################################################################################

main() {
    # Проверяем количество аргументов
    if [[ $# -eq 0 ]]; then
        usage
        exit 1
    fi
    
    local command="$1"
    shift
    
    case "$command" in
        init)
            init_directories
            echo -e "${GREEN}Директории инициализированы${NC}"
            ;;
        start)
            if [[ $# -ne 2 ]]; then
                echo -e "${RED}Ошибка: требуется 2 параметра (username, ip)${NC}"
                exit 1
            fi
            init_directories
            local sid=$(log_session_start "$(generate_sid "$2" "$1")" "$2" "$1" "22")
            echo "$sid"
            ;;
        end)
            if [[ $# -ne 1 ]]; then
                echo -e "${RED}Ошибка: требуется SID${NC}"
                exit 1
            fi
            log_session_end "$1"
            echo -e "${GREEN}Сессия $1 завершена${NC}"
            ;;
        list)
            list_active_sessions
            ;;
        show)
            if [[ $# -ne 1 ]]; then
                echo -e "${RED}Ошибка: требуется SID${NC}"
                exit 1
            fi
            show_session_details "$1"
            ;;
        current)
            local sid=$(get_current_sid)
            if [[ -n "$sid" ]]; then
                echo "$sid"
            else
                echo -e "${YELLOW}Не удалось определить текущий SID${NC}"
                exit 1
            fi
            ;;
        install-pam)
            if [[ $EUID -ne 0 ]]; then
                echo -e "${RED}Ошибка: требуются права root${NC}"
                exit 1
            fi
            install_pam_hooks
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            echo -e "${RED}Неизвестная команда: $command${NC}"
            usage
            exit 1
            ;;
    esac
}

# Запуск
main "$@"
