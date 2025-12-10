#!/bin/bash
################################################################################
# WIN_CONFIG AUTOMATION v1.0
# Автор: Sandrick Tech
# Дата: 2024-12-08
# Описание: Автоматическая генерация SSH config для Windows клиентов
#           с поддержкой ProxyJump через gate-пользователя
#
# Основной функционал:
#   - Автоматическое добавление блоков ProxyJump в win_config/config
#   - Генерация IdentityFile путей для каждого пользователя
#   - Поддержка множественных серверов
#   - Валидация и обновление существующих конфигов
#
# Структура:
#   /srv/sys/ssh/win_config/config - главный конфиг для Windows клиентов
#   /srv/sys/ssh/win_config/users/ - директория с индивидуальными конфигами
################################################################################

set -euo pipefail

################################################################################
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
################################################################################

# Базовая директория
WIN_CONFIG_DIR="/srv/sys/ssh/win_config"
CONFIG_FILE="$WIN_CONFIG_DIR/config"
USERS_DIR="$WIN_CONFIG_DIR/users"

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

################################################################################
# УТИЛИТЫ
################################################################################

info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

################################################################################
# ИНИЦИАЛИЗАЦИЯ
################################################################################

###
# Функция: init_win_config_structure
# Описание: Создание структуры директорий для win_config
###
init_win_config_structure() {
    info "Инициализация структуры win_config..."
    
    mkdir -p "$WIN_CONFIG_DIR"
    mkdir -p "$USERS_DIR"
    
    # Создаём базовый конфиг если не существует
    if [[ ! -f "$CONFIG_FILE" ]]; then
        cat > "$CONFIG_FILE" <<'EOF'
# SSH Config для Windows клиентов
# Автоматически генерируется скриптом win-config-automation.sh
# Дата создания: $(date '+%Y-%m-%d %H:%M:%S')
#
# Использование:
#   1. Скопируйте этот файл в C:\Users\<YourUsername>\.ssh\config
#   2. Убедитесь что у вас есть приватные ключи в C:\Users\<YourUsername>\.ssh\
#   3. Подключайтесь командой: ssh <hostname>

# ═══════════════════════════════════════════════════════════════════════
# ГЛОБАЛЬНЫЕ НАСТРОЙКИ
# ═══════════════════════════════════════════════════════════════════════

# Включаем сжатие для ускорения передачи данных
Compression yes

# Отключаем строгую проверку ключей для локальных сетей
# ВНИМАНИЕ: Для продакшн серверов используйте StrictHostKeyChecking yes
StrictHostKeyChecking no

# Отключаем добавление в known_hosts (опционально)
UserKnownHostsFile /dev/null

# Таймаут соединения
ConnectTimeout 10

# Keep-alive для предотвращения разрыва соединения
ServerAliveInterval 60
ServerAliveCountMax 3

# ═══════════════════════════════════════════════════════════════════════
# GATE SERVER (Прокси-сервер для ProxyJump)
# ═══════════════════════════════════════════════════════════════════════

EOF
        info "Создан базовый конфиг: $CONFIG_FILE"
    fi
    
    chmod 644 "$CONFIG_FILE"
    chmod 755 "$WIN_CONFIG_DIR"
    chmod 755 "$USERS_DIR"
    
    info "Структура win_config инициализирована"
}

################################################################################
# ГЕНЕРАЦИЯ БЛОКОВ КОНФИГА
################################################################################

###
# Функция: add_gate_server
# Описание: Добавление gate-сервера (если ещё не добавлен)
# Параметры:
#   $1 - IP/hostname gate-сервера
#   $2 - SSH порт gate-сервера
#   $3 - имя gate-пользователя (обычно "gate")
###
add_gate_server() {
    local gate_host="$1"
    local gate_port="${2:-22}"
    local gate_user="${3:-gate}"
    
    # Проверяем, не добавлен ли уже gate
    if grep -q "^Host gate$" "$CONFIG_FILE"; then
        warn "Gate-сервер уже добавлен в конфиг"
        return 0
    fi
    
    info "Добавление gate-сервера: $gate_user@$gate_host:$gate_port"
    
    cat >> "$CONFIG_FILE" <<EOF

# Gate Server - точка входа для всех подключений
Host gate
    HostName $gate_host
    User $gate_user
    Port $gate_port
    IdentityFile ~/.ssh/gate_key
    # Отключаем форвардинг агента для безопасности
    ForwardAgent no
    # Отключаем X11 forwarding
    ForwardX11 no
    # Включаем keep-alive
    ServerAliveInterval 60

EOF
    
    info "Gate-сервер добавлен в конфиг"
}

###
# Функция: add_user_to_config
# Описание: Добавление пользователя в главный конфиг с ProxyJump
# Параметры:
#   $1 - username (имя пользователя на сервере)
#   $2 - hostname (уникальное имя для SSH подключения)
#   $3 - server_ip (IP адрес сервера)
#   $4 - ssh_port (SSH порт сервера, по умолчанию 22)
#   $5 - use_proxyjump (использовать ли ProxyJump, по умолчанию true)
###
add_user_to_config() {
    local username="$1"
    local hostname="$2"
    local server_ip="$3"
    local ssh_port="${4:-22}"
    local use_proxyjump="${5:-true}"
    
    info "Добавление пользователя $username для подключения к $hostname ($server_ip)"
    
    # Проверяем, не добавлен ли уже этот хост
    if grep -q "^Host $hostname$" "$CONFIG_FILE"; then
        warn "Хост $hostname уже существует в конфиге"
        return 0
    fi
    
    # Добавляем разделитель
    cat >> "$CONFIG_FILE" <<EOF

# ═══════════════════════════════════════════════════════════════════════
# USER: $username @ $hostname
# ═══════════════════════════════════════════════════════════════════════

EOF
    
    # Генерируем блок конфига
    if [[ "$use_proxyjump" == "true" ]]; then
        cat >> "$CONFIG_FILE" <<EOF
Host $hostname
    HostName $server_ip
    User $username
    Port $ssh_port
    # Используем gate-сервер как прокси
    ProxyJump gate
    # Путь к приватному ключу пользователя
    IdentityFile ~/.ssh/${username}_key
    # Forwarding
    ForwardAgent no
    ForwardX11 no
    # Keep-alive
    ServerAliveInterval 60
    ServerAliveCountMax 3

EOF
    else
        # Прямое подключение без ProxyJump
        cat >> "$CONFIG_FILE" <<EOF
Host $hostname
    HostName $server_ip
    User $username
    Port $ssh_port
    # Прямое подключение (без ProxyJump)
    IdentityFile ~/.ssh/${username}_key
    # Forwarding
    ForwardAgent no
    ForwardX11 no
    # Keep-alive
    ServerAliveInterval 60
    ServerAliveCountMax 3

EOF
    fi
    
    info "Пользователь $username добавлен в конфиг как $hostname"
    
    # Создаём индивидуальный конфиг для пользователя
    create_user_config "$username" "$hostname" "$server_ip" "$ssh_port" "$use_proxyjump"
}

###
# Функция: create_user_config
# Описание: Создание индивидуального конфиг-файла для пользователя
# Параметры:
#   $1 - username
#   $2 - hostname
#   $3 - server_ip
#   $4 - ssh_port
#   $5 - use_proxyjump
###
create_user_config() {
    local username="$1"
    local hostname="$2"
    local server_ip="$3"
    local ssh_port="$4"
    local use_proxyjump="$5"
    
    local user_config="$USERS_DIR/${username}_config"
    
    cat > "$user_config" <<EOF
# SSH Config для пользователя: $username
# Дата создания: $(date '+%Y-%m-%d %H:%M:%S')
#
# Использование:
#   ssh -F $user_config $hostname

# Глобальные настройки
Compression yes
StrictHostKeyChecking no
UserKnownHostsFile /dev/null
ConnectTimeout 10
ServerAliveInterval 60
ServerAliveCountMax 3

EOF
    
    if [[ "$use_proxyjump" == "true" ]]; then
        cat >> "$user_config" <<EOF
# Gate Server
Host gate
    HostName $(grep -A 1 '^Host gate$' "$CONFIG_FILE" | grep HostName | awk '{print $2}')
    User gate
    Port $(grep -A 3 '^Host gate$' "$CONFIG_FILE" | grep Port | awk '{print $2}')
    IdentityFile ~/.ssh/gate_key
    ForwardAgent no
    ForwardX11 no

EOF
    fi
    
    cat >> "$user_config" <<EOF
# Main Server
Host $hostname
    HostName $server_ip
    User $username
    Port $ssh_port
EOF
    
    if [[ "$use_proxyjump" == "true" ]]; then
        echo "    ProxyJump gate" >> "$user_config"
    fi
    
    cat >> "$user_config" <<EOF
    IdentityFile ~/.ssh/${username}_key
    ForwardAgent no
    ForwardX11 no
    ServerAliveInterval 60

EOF
    
    chmod 644 "$user_config"
    info "Создан индивидуальный конфиг: $user_config"
}

################################################################################
# УДАЛЕНИЕ И ОБНОВЛЕНИЕ
################################################################################

###
# Функция: remove_user_from_config
# Описание: Удаление пользователя из конфига
# Параметры:
#   $1 - hostname
###
remove_user_from_config() {
    local hostname="$1"
    
    info "Удаление хоста $hostname из конфига..."
    
    # Создаём резервную копию
    cp "$CONFIG_FILE" "${CONFIG_FILE}.backup_$(date +%Y%m%d_%H%M%S)"
    
    # Удаляем блок конфига (между двумя разделителями)
    # Это сложная операция, используем временный файл
    local temp_file=$(mktemp)
    local in_block=0
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^Host[[:space:]]+$hostname$ ]]; then
            in_block=1
            continue
        fi
        
        if [[ $in_block -eq 1 ]]; then
            # Проверяем начало следующего блока
            if [[ "$line" =~ ^Host[[:space:]] || "$line" =~ ^#.*═══ ]]; then
                in_block=0
            else
                continue
            fi
        fi
        
        echo "$line" >> "$temp_file"
    done < "$CONFIG_FILE"
    
    mv "$temp_file" "$CONFIG_FILE"
    
    info "Хост $hostname удалён из конфига"
}

###
# Функция: list_configured_users
# Описание: Показать всех пользователей в конфиге
###
list_configured_users() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}          НАСТРОЕННЫЕ ПОЛЬЗОВАТЕЛИ                          ${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    grep '^Host ' "$CONFIG_FILE" | grep -v '^Host gate$' | while read -r line; do
        local hostname=$(echo "$line" | awk '{print $2}')
        local hostip=$(grep -A 1 "^Host $hostname$" "$CONFIG_FILE" | grep HostName | awk '{print $2}')
        local user=$(grep -A 2 "^Host $hostname$" "$CONFIG_FILE" | grep User | awk '{print $2}')
        local port=$(grep -A 3 "^Host $hostname$" "$CONFIG_FILE" | grep Port | awk '{print $2}')
        local proxyjump=$(grep -A 5 "^Host $hostname$" "$CONFIG_FILE" | grep ProxyJump | awk '{print $2}')
        
        echo -e "${GREEN}[HOST]${NC} $hostname"
        echo "  User: $user"
        echo "  Server: $hostip:$port"
        echo "  ProxyJump: ${proxyjump:-"Нет (прямое подключение)"}"
        echo ""
    done
}

################################################################################
# CLI ИНТЕРФЕЙС
################################################################################

usage() {
    cat <<EOF
Win_Config Automation v1.0 - Автоматическая генерация SSH config

Использование:
  $0 <команда> [параметры]

Команды:
  init                              - Инициализация структуры win_config
  add-gate <ip> [port] [user]       - Добавить gate-сервер
  add-user <user> <hostname> <ip> [port] [proxyjump] - Добавить пользователя
  remove <hostname>                 - Удалить хост из конфига
  list                              - Показать всех настроенных пользователей
  export                            - Экспортировать конфиг в текущую директорию
  help                              - Показать эту справку

Примеры:
  $0 init
  $0 add-gate 203.0.113.10 22 gate
  $0 add-user john myserver 192.168.1.100 22 true
  $0 add-user alice directserver 10.0.0.50 2222 false
  $0 list
  $0 remove myserver
  $0 export

EOF
}

################################################################################
# ГЛАВНАЯ ФУНКЦИЯ
################################################################################

main() {
    if [[ $# -eq 0 ]]; then
        usage
        exit 1
    fi
    
    local command="$1"
    shift
    
    case "$command" in
        init)
            init_win_config_structure
            ;;
        add-gate)
            if [[ $# -lt 1 ]]; then
                error "Требуется IP gate-сервера"
                exit 1
            fi
            init_win_config_structure
            add_gate_server "$1" "${2:-22}" "${3:-gate}"
            ;;
        add-user)
            if [[ $# -lt 3 ]]; then
                error "Требуется: username, hostname, server_ip"
                exit 1
            fi
            init_win_config_structure
            add_user_to_config "$1" "$2" "$3" "${4:-22}" "${5:-true}"
            ;;
        remove)
            if [[ $# -ne 1 ]]; then
                error "Требуется hostname"
                exit 1
            fi
            remove_user_from_config "$1"
            ;;
        list)
            list_configured_users
            ;;
        export)
            local export_file="./ssh_config_export_$(date +%Y%m%d_%H%M%S)"
            cp "$CONFIG_FILE" "$export_file"
            info "Конфиг экспортирован: $export_file"
            echo ""
            echo -e "${YELLOW}Инструкции для Windows:${NC}"
            echo "1. Скопируйте файл $export_file"
            echo "2. Переименуйте в 'config' (без расширения)"
            echo "3. Поместите в C:\\Users\\<YourUsername>\\.ssh\\config"
            echo "4. Скопируйте приватные ключи в C:\\Users\\<YourUsername>\\.ssh\\"
            echo "5. Подключайтесь: ssh <hostname>"
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            error "Неизвестная команда: $command"
            usage
            exit 1
            ;;
    esac
}

main "$@"
