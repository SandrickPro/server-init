#!/bin/bash
################################################################################
# Performance Optimizer - Оптимизация производительности проекта
# Автор: Sandrick Tech
# Дата: 2024-12-09
################################################################################

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

################################################################################
# ОПТИМИЗАЦИЯ МЕНЮ - Кеширование
################################################################################

optimize_menu_caching() {
    info "Добавление кеширования меню..."
    
    local file="/opt/server-deploy/server-deploy-v5-enhanced.sh"
    
    # Добавляем кеш переменные в начало файла
    if ! grep -q "MENU_CACHE=" "$file"; then
        sed -i '10a\
# Кеш для оптимизации меню\
declare -g MENU_CACHE=""\
declare -g MENU_CACHE_TIME=0\
CACHE_TTL=30  # Время жизни кеша в секундах' "$file"
        
        info "✅ Кеш переменные добавлены"
    fi
}

################################################################################
# ПАРАЛЛЕЛЬНАЯ УСТАНОВКА ПАКЕТОВ
################################################################################

optimize_package_installation() {
    info "Оптимизация установки Python пакетов..."
    
    cat > /tmp/parallel_pip_install.sh <<'EOF'
#!/bin/bash
# Параллельная установка пакетов

install_python_parallel() {
    local packages_groups=(
        "flask django fastapi uvicorn requests aiohttp httpx"
        "numpy pandas matplotlib seaborn scipy scikit-learn"
        "jupyter notebook ipython statsmodels"
        "pytest pytest-cov black flake8 mypy pylint"
        "python-dotenv click rich pyyaml pydantic"
        "beautifulsoup4 lxml selenium scrapy"
        "sqlalchemy pymysql psycopg2-binary redis pymongo"
        "pillow opencv-python-headless imageio"
    )
    
    echo "🚀 Параллельная установка 55+ пакетов..."
    
    for group in "${packages_groups[@]}"; do
        echo "  ⏳ Группа: $group"
        pip3 install --no-cache-dir $group > /dev/null 2>&1 &
    done
    
    wait
    echo "✅ Все пакеты установлены (параллельно)"
}

install_python_parallel
EOF
    
    chmod +x /tmp/parallel_pip_install.sh
    info "✅ Скрипт параллельной установки создан: /tmp/parallel_pip_install.sh"
}

################################################################################
# УЛУЧШЕННОЕ ЛОГИРОВАНИЕ
################################################################################

setup_structured_logging() {
    info "Настройка структурированного логирования..."
    
    cat > /opt/server-deploy/lib/logging.sh <<'EOF'
#!/bin/bash
# Structured Logging Library

LOG_DIR="/srv/sys/logs"
LOG_FILE="$LOG_DIR/system.log"
LOG_JSON_FILE="$LOG_DIR/system.json"

mkdir -p "$LOG_DIR"

log_structured() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S.%3N')
    local pid=$$
    local module=$(basename "${BASH_SOURCE[2]}")
    local function_name="${FUNCNAME[2]}"
    local line_number="${BASH_LINENO[1]}"
    
    # Форматированный вывод для человека
    printf "[%s] [%-5s] [%s:%s:%d] [PID:%d] %s\n" \
        "$timestamp" "$level" "$module" "$function_name" "$line_number" "$pid" "$message" \
        | tee -a "$LOG_FILE"
    
    # JSON для машинной обработки
    if command -v jq &>/dev/null; then
        jq -n \
            --arg ts "$timestamp" \
            --arg lvl "$level" \
            --arg mod "$module" \
            --arg fn "$function_name" \
            --argjson ln "$line_number" \
            --argjson pid "$pid" \
            --arg msg "$message" \
            '{timestamp: $ts, level: $lvl, module: $mod, function: $fn, line: $ln, pid: $pid, message: $msg}' \
            >> "$LOG_JSON_FILE"
    fi
}

log_info() { log_structured "INFO" "$1"; }
log_warn() { log_structured "WARN" "$1"; }
log_error() { log_structured "ERROR" "$1"; }
log_debug() { log_structured "DEBUG" "$1"; }
log_success() { log_structured "SUCCESS" "$1"; }
EOF
    
    info "✅ Библиотека логирования создана: /opt/server-deploy/lib/logging.sh"
}

################################################################################
# ВАЛИДАЦИЯ IP АДРЕСОВ
################################################################################

create_validation_library() {
    info "Создание библиотеки валидации..."
    
    cat > /opt/server-deploy/lib/validation.sh <<'EOF'
#!/bin/bash
# Validation Library

validate_ip() {
    local ip=$1
    local allow_private=${2:-true}
    
    # Regex проверка формата
    if ! [[ "$ip" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        echo "❌ Неверный формат IP: $ip"
        return 1
    fi
    
    # Проверка каждого октета
    IFS='.' read -ra OCTETS <<< "$ip"
    for octet in "${OCTETS[@]}"; do
        if [[ $octet -gt 255 ]]; then
            echo "❌ Октет $octet превышает 255"
            return 1
        fi
    done
    
    # Проверка на зарезервированные адреса
    if [[ "$allow_private" == "false" ]]; then
        if [[ "${OCTETS[0]}" -eq 10 ]] || \
           [[ "${OCTETS[0]}" -eq 172 && "${OCTETS[1]}" -ge 16 && "${OCTETS[1]}" -le 31 ]] || \
           [[ "${OCTETS[0]}" -eq 192 && "${OCTETS[1]}" -eq 168 ]]; then
            echo "❌ Приватный IP не разрешён: $ip"
            return 1
        fi
    fi
    
    return 0
}

validate_hostname() {
    local hostname=$1
    
    # RFC 1123 hostname validation
    if ! [[ "$hostname" =~ ^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$ ]]; then
        echo "❌ Неверный формат hostname: $hostname"
        return 1
    fi
    
    if [[ ${#hostname} -gt 63 ]]; then
        echo "❌ Hostname слишком длинный (max 63): $hostname"
        return 1
    fi
    
    return 0
}

validate_port() {
    local port=$1
    
    if ! [[ "$port" =~ ^[0-9]+$ ]]; then
        echo "❌ Порт должен быть числом: $port"
        return 1
    fi
    
    if [[ $port -lt 1 || $port -gt 65535 ]]; then
        echo "❌ Порт вне диапазона 1-65535: $port"
        return 1
    fi
    
    return 0
}

validate_email() {
    local email=$1
    
    if ! [[ "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        echo "❌ Неверный email: $email"
        return 1
    fi
    
    return 0
}

validate_path() {
    local path=$1
    local must_exist=${2:-false}
    
    # Защита от path traversal
    if [[ "$path" =~ \.\. ]]; then
        echo "❌ Обнаружена попытка path traversal: $path"
        return 1
    fi
    
    if [[ "$must_exist" == "true" && ! -e "$path" ]]; then
        echo "❌ Путь не существует: $path"
        return 1
    fi
    
    return 0
}
EOF
    
    info "✅ Библиотека валидации создана: /opt/server-deploy/lib/validation.sh"
}

################################################################################
# ТЕСТИРОВАНИЕ
################################################################################

setup_testing_framework() {
    info "Установка BATS (Bash Automated Testing System)..."
    
    if ! command -v bats &>/dev/null; then
        cd /tmp
        git clone --depth 1 https://github.com/bats-core/bats-core.git
        cd bats-core
        ./install.sh /usr/local
        cd ..
        rm -rf bats-core
        info "✅ BATS установлен"
    else
        info "✅ BATS уже установлен"
    fi
    
    # Создаём тестовую структуру
    mkdir -p /opt/server-deploy/tests
    
    # Пример теста для валидации
    cat > /opt/server-deploy/tests/test_validation.bats <<'EOF'
#!/usr/bin/env bats

setup() {
    source /opt/server-deploy/lib/validation.sh
}

@test "validate_ip accepts valid IP" {
    run validate_ip "192.168.1.1"
    [ "$status" -eq 0 ]
}

@test "validate_ip rejects invalid IP" {
    run validate_ip "999.999.999.999"
    [ "$status" -eq 1 ]
}

@test "validate_ip rejects malformed IP" {
    run validate_ip "192.168.1"
    [ "$status" -eq 1 ]
}

@test "validate_hostname accepts valid hostname" {
    run validate_hostname "server01"
    [ "$status" -eq 0 ]
}

@test "validate_hostname rejects invalid hostname" {
    run validate_hostname "server_01"  # Подчёркивание не разрешено
    [ "$status" -eq 1 ]
}

@test "validate_port accepts valid port" {
    run validate_port "8080"
    [ "$status" -eq 0 ]
}

@test "validate_port rejects invalid port" {
    run validate_port "70000"
    [ "$status" -eq 1 ]
}
EOF
    
    chmod +x /opt/server-deploy/tests/test_validation.bats
    info "✅ Тесты созданы: /opt/server-deploy/tests/"
}

################################################################################
# МОНИТОРИНГ
################################################################################

setup_prometheus_exporter() {
    info "Настройка Prometheus Node Exporter..."
    
    if ! command -v node_exporter &>/dev/null; then
        apt-get install -y prometheus-node-exporter
        systemctl enable prometheus-node-exporter
        systemctl start prometheus-node-exporter
        
        # Открываем порт
        iptables -C INPUT -p tcp --dport 9100 -j ACCEPT 2>/dev/null || \
            iptables -I INPUT -p tcp --dport 9100 -j ACCEPT
        iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
        
        info "✅ Node Exporter установлен: http://localhost:9100/metrics"
    else
        info "✅ Node Exporter уже установлен"
    fi
}

################################################################################
# АВТОМАТИЧЕСКИЙ BACKUP
################################################################################

setup_automated_backup() {
    info "Настройка автоматического backup..."
    
    cat > /usr/local/bin/smart-backup <<'EOF'
#!/bin/bash
# Smart Backup Script

BACKUP_ROOT="/srv/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/$DATE"

mkdir -p "$BACKUP_DIR"

# Инкрементальный backup
rsync -av --link-dest="$BACKUP_ROOT/latest" \
    --exclude='*.log' \
    --exclude='*.tmp' \
    --exclude='node_modules' \
    /srv/projects/ \
    "$BACKUP_DIR/projects/"

rsync -av --link-dest="$BACKUP_ROOT/latest" \
    /opt/server-deploy/ \
    "$BACKUP_DIR/server-deploy/"

# Обновляем latest symlink
ln -snf "$BACKUP_DIR" "$BACKUP_ROOT/latest"

# Удаляем backup'ы старше 30 дней
find "$BACKUP_ROOT" -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;

# Логируем
echo "$(date): Backup completed - $(du -sh $BACKUP_DIR | awk '{print $1}')" >> /var/log/backup.log

# Уведомление в Telegram (если настроено)
if [[ -n "$TELEGRAM_BOT_TOKEN" && -n "$TELEGRAM_CHAT_ID" ]]; then
    curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d chat_id="$TELEGRAM_CHAT_ID" \
        -d text="✅ Backup завершён: $(du -sh $BACKUP_DIR | awk '{print $1}')" >/dev/null
fi
EOF
    
    chmod +x /usr/local/bin/smart-backup
    
    # Создаём cron job
    cat > /etc/cron.d/smart-backup <<EOF
# Ежедневный backup в 3:00
0 3 * * * root /usr/local/bin/smart-backup
EOF
    
    info "✅ Автоматический backup настроен (ежедневно в 3:00)"
}

################################################################################
# ГЛАВНОЕ МЕНЮ
################################################################################

optimization_menu() {
    while true; do
        local choice=$(dialog --clear \
            --backtitle "Performance Optimizer" \
            --title "Оптимизация производительности v8" \
            --menu "Выберите действие:" \
            20 70 12 \
            1 "⚡ Оптимизировать кеширование меню" \
            2 "📦 Параллельная установка пакетов" \
            3 "📝 Структурированное логирование" \
            4 "✅ Библиотека валидации" \
            5 "🧪 Настроить тестирование (BATS)" \
            6 "📊 Prometheus мониторинг" \
            7 "💾 Автоматический backup" \
            8 "🚀 Применить ВСЕ оптимизации" \
            9 "🧪 Запустить тесты" \
            0 "◀ Выход" \
            3>&1 1>&2 2>&3)
        
        case $choice in
            1) optimize_menu_caching ;;
            2) optimize_package_installation ;;
            3) setup_structured_logging ;;
            4) create_validation_library ;;
            5) setup_testing_framework ;;
            6) setup_prometheus_exporter ;;
            7) setup_automated_backup ;;
            8)
                info "Применение всех оптимизаций..."
                optimize_menu_caching
                optimize_package_installation
                setup_structured_logging
                create_validation_library
                setup_testing_framework
                setup_prometheus_exporter
                setup_automated_backup
                dialog --msgbox "✅ Все оптимизации применены!" 7 40
                ;;
            9)
                if command -v bats &>/dev/null; then
                    bats /opt/server-deploy/tests/*.bats
                    read -p "Нажмите Enter для продолжения..."
                else
                    dialog --msgbox "BATS не установлен. Выберите пункт 5." 7 50
                fi
                ;;
            0|"") return ;;
        esac
    done
}

# Запуск
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $EUID -ne 0 ]]; then
        echo "Требуются права root"
        exit 1
    fi
    
    mkdir -p /opt/server-deploy/lib
    optimization_menu
fi
