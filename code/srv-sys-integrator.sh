#!/bin/bash
################################################################################
# SRV-SYS INTEGRATOR v1.0
# Автор: Sandrick Tech
# Дата: 2024-12-09
# Описание: Централизованный интегратор всех компонентов системы
#
# Основной функционал:
#   - Автоматическая инициализация всей структуры /srv/sys/
#   - Интеграция всех компонентов между собой
#   - Автоматическое обнаружение установленных сервисов
#   - Генерация конфигураций на основе реального состояния системы
#   - Синхронизация между iptables, systemd, SSH конфигами
#   - Централизованное управление через единый JSON манифест
#
# Архитектура /srv/sys/:
#   /srv/sys/
#   ├── manifest.json           # Главный манифест системы
#   ├── configs/                # Конфигурации всех сервисов
#   ├── iptables/               # Правила firewall
#   ├── systemd/                # systemd units
#   ├── ssh/                    # SSH конфиги и сессии
#   ├── backups/                # Резервные копии
#   ├── scripts/                # Вспомогательные скрипты
#   ├── logs/                   # Централизованные логи
#   └── hooks/                  # Хуки для интеграции
################################################################################

set -euo pipefail

################################################################################
# ГЛОБАЛЬНЫЕ КОНСТАНТЫ
################################################################################

# Базовый путь системы
readonly SRV_SYS="/srv/sys"

# Подкаталоги
readonly SRV_CONFIGS="$SRV_SYS/configs"
readonly SRV_IPTABLES="$SRV_SYS/iptables"
readonly SRV_SYSTEMD="$SRV_SYS/systemd"
readonly SRV_SSH="$SRV_SYS/ssh"
readonly SRV_BACKUPS="$SRV_SYS/backups"
readonly SRV_SCRIPTS="$SRV_SYS/scripts"
readonly SRV_LOGS="$SRV_SYS/logs"
readonly SRV_HOOKS="$SRV_SYS/hooks"

# Манифест системы
readonly MANIFEST="$SRV_SYS/manifest.json"

# Логи
readonly INTEGRATOR_LOG="$SRV_LOGS/integrator.log"
readonly CHANGES_LOG="$SRV_LOGS/changes.log"

# Цвета
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly MAGENTA='\033[0;35m'
readonly NC='\033[0m'

################################################################################
# УТИЛИТЫ
################################################################################

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$INTEGRATOR_LOG"
}

info() {
    echo -e "${GREEN}[✓]${NC} $*"
    log "INFO" "$*"
}

warn() {
    echo -e "${YELLOW}[!]${NC} $*"
    log "WARN" "$*"
}

error() {
    echo -e "${RED}[✗]${NC} $*"
    log "ERROR" "$*"
}

step() {
    echo -e "${CYAN}[→]${NC} $*"
    log "STEP" "$*"
}

success() {
    echo -e "${MAGENTA}[★]${NC} $*"
    log "SUCCESS" "$*"
}

banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              SRV-SYS INTEGRATOR v1.0                              ║
║                                                                   ║
║          Централизованная интеграция всех компонентов             ║
║                    /srv/sys/ архитектура                          ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

################################################################################
# ИНИЦИАЛИЗАЦИЯ СТРУКТУРЫ
################################################################################

init_directory_structure() {
    step "Инициализация структуры директорий /srv/sys/"
    
    # Создаём базовую структуру
    local dirs=(
        "$SRV_SYS"
        "$SRV_CONFIGS"
        "$SRV_CONFIGS/nginx"
        "$SRV_CONFIGS/mysql"
        "$SRV_CONFIGS/postgresql"
        "$SRV_CONFIGS/redis"
        "$SRV_CONFIGS/mongodb"
        "$SRV_CONFIGS/fail2ban"
        "$SRV_CONFIGS/ssh"
        "$SRV_IPTABLES"
        "$SRV_IPTABLES/v4"
        "$SRV_IPTABLES/v6"
        "$SRV_SYSTEMD"
        "$SRV_SYSTEMD/system"
        "$SRV_SSH"
        "$SRV_SSH/win_config"
        "$SRV_SSH/ssh_session"
        "$SRV_SSH/ssh_session/active"
        "$SRV_SSH/ssh_session/archive"
        "$SRV_SSH/ssh_session/metadata"
        "$SRV_SSH/sshd_config.d"
        "$SRV_SSH/authorized_keys"
        "$SRV_BACKUPS"
        "$SRV_BACKUPS/configs"
        "$SRV_BACKUPS/iptables"
        "$SRV_BACKUPS/ssh"
        "$SRV_SCRIPTS"
        "$SRV_SCRIPTS/deploy"
        "$SRV_SCRIPTS/maintenance"
        "$SRV_SCRIPTS/monitoring"
        "$SRV_LOGS"
        "$SRV_HOOKS"
        "$SRV_HOOKS/pre-deploy"
        "$SRV_HOOKS/post-deploy"
        "$SRV_HOOKS/pre-update"
        "$SRV_HOOKS/post-update"
    )
    
    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            chmod 755 "$dir"
        fi
    done
    
    # Специальные права для чувствительных директорий
    chmod 700 "$SRV_SSH/ssh_session"
    chmod 700 "$SRV_SSH/authorized_keys"
    chmod 755 "$SRV_BACKUPS"
    
    info "Структура директорий создана"
}

################################################################################
# МАНИФЕСТ СИСТЕМЫ
################################################################################

create_manifest() {
    step "Создание манифеста системы"
    
    if [[ -f "$MANIFEST" ]]; then
        warn "Манифест уже существует, создаём резервную копию"
        cp "$MANIFEST" "$SRV_BACKUPS/manifest.json.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    cat > "$MANIFEST" <<'MANIFEST_EOF'
{
  "version": "1.0",
  "created": "TIMESTAMP",
  "updated": "TIMESTAMP",
  "system": {
    "hostname": "",
    "ip_address": "",
    "os": "",
    "kernel": ""
  },
  "components": {
    "iptables": {
      "enabled": true,
      "version": "",
      "config_path": "/srv/sys/iptables",
      "combined_v4": "/srv/sys/iptables/v4/combined.v4",
      "combined_v6": "/srv/sys/iptables/v6/combined.v6"
    },
    "ssh": {
      "enabled": true,
      "port": 22,
      "config_path": "/srv/sys/ssh",
      "gate_enabled": false,
      "gate_user": "gate",
      "sid_enabled": false
    },
    "fail2ban": {
      "enabled": false,
      "config_path": "/srv/sys/configs/fail2ban"
    },
    "nginx": {
      "enabled": false,
      "config_path": "/srv/sys/configs/nginx",
      "sites_available": "/srv/sys/configs/nginx/sites-available",
      "sites_enabled": "/srv/sys/configs/nginx/sites-enabled"
    },
    "mysql": {
      "enabled": false,
      "config_path": "/srv/sys/configs/mysql",
      "data_dir": ""
    },
    "postgresql": {
      "enabled": false,
      "config_path": "/srv/sys/configs/postgresql",
      "data_dir": ""
    },
    "redis": {
      "enabled": false,
      "config_path": "/srv/sys/configs/redis"
    },
    "mongodb": {
      "enabled": false,
      "config_path": "/srv/sys/configs/mongodb",
      "data_dir": ""
    }
  },
  "services": {},
  "ports": {},
  "users": {},
  "backups": {
    "enabled": true,
    "path": "/srv/sys/backups",
    "retention_days": 30
  },
  "integration": {
    "auto_sync": true,
    "hooks_enabled": true
  }
}
MANIFEST_EOF
    
    # Заполняем реальные значения
    local timestamp=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
    local hostname=$(hostname)
    local ip_address=$(hostname -I | awk '{print $1}')
    local os=$(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)
    local kernel=$(uname -r)
    
    # Используем jq для обновления JSON (если установлен)
    if command -v jq &>/dev/null; then
        jq --arg ts "$timestamp" \
           --arg host "$hostname" \
           --arg ip "$ip_address" \
           --arg os "$os" \
           --arg kern "$kernel" \
           '.created = $ts | .updated = $ts | 
            .system.hostname = $host | 
            .system.ip_address = $ip | 
            .system.os = $os | 
            .system.kernel = $kern' \
           "$MANIFEST" > "$MANIFEST.tmp" && mv "$MANIFEST.tmp" "$MANIFEST"
    fi
    
    info "Манифест создан: $MANIFEST"
}

################################################################################
# ОБНАРУЖЕНИЕ СЕРВИСОВ
################################################################################

discover_services() {
    step "Обнаружение установленных сервисов"
    
    local services_found=0
    
    # Проверяем наличие сервисов
    local -A SERVICE_CHECKS=(
        ["nginx"]="nginx -v"
        ["apache2"]="apache2 -v"
        ["mysql"]="mysql --version"
        ["mariadb"]="mariadb --version"
        ["postgresql"]="psql --version"
        ["redis"]="redis-server --version"
        ["mongodb"]="mongod --version"
        ["docker"]="docker --version"
        ["fail2ban"]="fail2ban-server --version"
        ["iptables"]="iptables --version"
    )
    
    for service in "${!SERVICE_CHECKS[@]}"; do
        if command -v "${SERVICE_CHECKS[$service]%% *}" &>/dev/null; then
            info "  Обнаружен: $service"
            ((services_found++))
            
            # Сохраняем в манифест
            if command -v jq &>/dev/null; then
                jq --arg svc "$service" \
                   '.components[$svc].enabled = true' \
                   "$MANIFEST" > "$MANIFEST.tmp" && mv "$MANIFEST.tmp" "$MANIFEST" 2>/dev/null || true
            fi
        fi
    done
    
    success "Обнаружено сервисов: $services_found"
}

################################################################################
# ИНТЕГРАЦИЯ КОМПОНЕНТОВ
################################################################################

integrate_iptables() {
    step "Интеграция iptables контроллера"
    
    # Копируем скрипт в /srv/sys/scripts/
    if [[ -f "/root/srv-sys-iptables-controller.sh" ]]; then
        cp "/root/srv-sys-iptables-controller.sh" "$SRV_SCRIPTS/iptables-controller.sh"
        chmod +x "$SRV_SCRIPTS/iptables-controller.sh"
        
        # Создаём симлинк для удобства
        ln -sf "$SRV_SCRIPTS/iptables-controller.sh" "/usr/local/bin/iptables-controller"
        
        info "iptables контроллер интегрирован"
    else
        warn "iptables контроллер не найден"
    fi
    
    # Проверяем существование combined правил
    if [[ -f "$SRV_IPTABLES/v4/combined.v4" ]]; then
        info "  Combined правила IPv4: существуют"
    else
        warn "  Combined правила IPv4: не найдены"
    fi
}

integrate_ssh_sid() {
    step "Интеграция SID системы"
    
    # Копируем скрипты
    local scripts=(
        "ssh-sid-system.sh"
        "log_session_start.sh"
        "log_session_end.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [[ -f "/root/$script" ]]; then
            cp "/root/$script" "$SRV_SCRIPTS/$script"
            chmod +x "$SRV_SCRIPTS/$script"
        fi
    done
    
    # Создаём симлинки
    ln -sf "$SRV_SCRIPTS/ssh-sid-system.sh" "/usr/local/bin/ssh-sid"
    
    # Копируем systemd unit
    if [[ -f "/root/ssh-session@.service" ]]; then
        cp "/root/ssh-session@.service" "$SRV_SYSTEMD/system/"
    fi
    
    info "SID система интегрирована"
}

integrate_win_config() {
    step "Интеграция Win_Config автоматизации"
    
    if [[ -f "/root/win-config-automation.sh" ]]; then
        cp "/root/win-config-automation.sh" "$SRV_SCRIPTS/win-config.sh"
        chmod +x "$SRV_SCRIPTS/win-config.sh"
        
        ln -sf "$SRV_SCRIPTS/win-config.sh" "/usr/local/bin/win-config"
        
        info "Win_Config интегрирован"
    fi
}

integrate_security() {
    step "Интеграция модуля безопасности"
    
    if [[ -f "/root/security-hardening-advanced.sh" ]]; then
        cp "/root/security-hardening-advanced.sh" "$SRV_SCRIPTS/security-hardening.sh"
        chmod +x "$SRV_SCRIPTS/security-hardening.sh"
        
        ln -sf "$SRV_SCRIPTS/security-hardening.sh" "/usr/local/bin/security-hardening"
        
        info "Модуль безопасности интегрирован"
    fi
}

################################################################################
# АВТОКОНФИГУРАЦИЯ СЕРВИСОВ
################################################################################

auto_configure_nginx() {
    step "Автоконфигурация Nginx"
    
    if ! command -v nginx &>/dev/null; then
        warn "Nginx не установлен, пропускаем"
        return
    fi
    
    # Создаём директории для конфигов
    mkdir -p "$SRV_CONFIGS/nginx/sites-available"
    mkdir -p "$SRV_CONFIGS/nginx/sites-enabled"
    mkdir -p "$SRV_CONFIGS/nginx/snippets"
    
    # Создаём базовый конфиг
    cat > "$SRV_CONFIGS/nginx/nginx.conf" <<'NGINX_EOF'
# Nginx конфигурация (управляется через /srv/sys/)
# Сгенерировано: srv-sys-integrator

user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
}

http {
    # Основные настройки
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # MIME типы
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Логи
    access_log /srv/sys/logs/nginx-access.log;
    error_log /srv/sys/logs/nginx-error.log;
    
    # Gzip сжатие
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    
    # Включаем сайты из /srv/sys/
    include /srv/sys/configs/nginx/sites-enabled/*;
}
NGINX_EOF
    
    info "Nginx автоконфигурирован"
}

auto_configure_mysql() {
    step "Автоконфигурация MySQL/MariaDB"
    
    if ! command -v mysql &>/dev/null; then
        warn "MySQL не установлен, пропускаем"
        return
    fi
    
    # Создаём директорию
    mkdir -p "$SRV_CONFIGS/mysql"
    
    # Базовый конфиг
    cat > "$SRV_CONFIGS/mysql/custom.cnf" <<'MYSQL_EOF'
# MySQL/MariaDB конфигурация (управляется через /srv/sys/)
# Сгенерировано: srv-sys-integrator

[mysqld]
# Базовые настройки
datadir = /var/lib/mysql
socket = /var/run/mysqld/mysqld.sock
pid-file = /var/run/mysqld/mysqld.pid

# Логирование
log_error = /srv/sys/logs/mysql-error.log
slow_query_log = 1
slow_query_log_file = /srv/sys/logs/mysql-slow.log
long_query_time = 2

# Безопасность
bind-address = 127.0.0.1
local-infile = 0

# Производительность
max_connections = 100
key_buffer_size = 16M
max_allowed_packet = 16M
thread_stack = 192K
thread_cache_size = 8
MYSQL_EOF
    
    info "MySQL автоконфигурирован"
}

auto_configure_postgresql() {
    step "Автоконфигурация PostgreSQL"
    
    if ! command -v psql &>/dev/null; then
        warn "PostgreSQL не установлен, пропускаем"
        return
    fi
    
    mkdir -p "$SRV_CONFIGS/postgresql"
    
    # Находим версию PostgreSQL
    local pg_version=$(psql --version | grep -oP '\d+' | head -1)
    
    cat > "$SRV_CONFIGS/postgresql/custom.conf" <<'PG_EOF'
# PostgreSQL конфигурация (управляется через /srv/sys/)
# Сгенерировано: srv-sys-integrator

# Подключение
listen_addresses = 'localhost'
max_connections = 100

# Логирование
log_destination = 'stderr'
logging_collector = on
log_directory = '/srv/sys/logs'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d '

# Безопасность
ssl = on
password_encryption = scram-sha-256
PG_EOF
    
    info "PostgreSQL автоконфигурирован"
}

################################################################################
# ХУКИ И АВТОМАТИЗАЦИЯ
################################################################################

create_hooks() {
    step "Создание хуков интеграции"
    
    # Pre-deploy хук
    cat > "$SRV_HOOKS/pre-deploy/00-backup.sh" <<'HOOK_EOF'
#!/bin/bash
# Pre-deploy хук: создание резервных копий
echo "[$(date)] Pre-deploy: создание backup конфигов..."
tar -czf /srv/sys/backups/pre-deploy-$(date +%Y%m%d_%H%M%S).tar.gz \
    /srv/sys/configs/ \
    /srv/sys/iptables/ \
    /srv/sys/ssh/ 2>/dev/null || true
HOOK_EOF
    
    # Post-deploy хук
    cat > "$SRV_HOOKS/post-deploy/00-reload.sh" <<'HOOK_EOF'
#!/bin/bash
# Post-deploy хук: перезагрузка сервисов
echo "[$(date)] Post-deploy: перезагрузка сервисов..."

# Перезагружаем systemd
systemctl daemon-reload 2>/dev/null || true

# Применяем iptables если существуют правила
if [[ -f /srv/sys/iptables/v4/combined.v4 ]]; then
    iptables-restore < /srv/sys/iptables/v4/combined.v4 2>/dev/null || true
fi

# Перезагружаем Nginx если установлен
if command -v nginx &>/dev/null; then
    nginx -t && systemctl reload nginx 2>/dev/null || true
fi
HOOK_EOF
    
    chmod +x "$SRV_HOOKS/pre-deploy/00-backup.sh"
    chmod +x "$SRV_HOOKS/post-deploy/00-reload.sh"
    
    info "Хуки созданы"
}

################################################################################
# СИНХРОНИЗАЦИЯ
################################################################################

sync_all_components() {
    step "Синхронизация всех компонентов"
    
    # Синхронизируем конфиги с системными
    sync_nginx_configs
    sync_mysql_configs
    sync_ssh_configs
    
    success "Синхронизация завершена"
}

sync_nginx_configs() {
    if [[ -d "$SRV_CONFIGS/nginx" ]] && command -v nginx &>/dev/null; then
        # Создаём симлинк на главный конфиг
        if [[ -f "$SRV_CONFIGS/nginx/nginx.conf" ]]; then
            ln -sf "$SRV_CONFIGS/nginx/nginx.conf" /etc/nginx/nginx.conf.d/srv-sys.conf 2>/dev/null || true
        fi
        info "  Nginx конфиги синхронизированы"
    fi
}

sync_mysql_configs() {
    if [[ -d "$SRV_CONFIGS/mysql" ]] && command -v mysql &>/dev/null; then
        # Симлинк на custom конфиг
        if [[ -f "$SRV_CONFIGS/mysql/custom.cnf" ]]; then
            ln -sf "$SRV_CONFIGS/mysql/custom.cnf" /etc/mysql/conf.d/srv-sys.cnf 2>/dev/null || true
        fi
        info "  MySQL конфиги синхронизированы"
    fi
}

sync_ssh_configs() {
    if [[ -d "$SRV_SSH/sshd_config.d" ]]; then
        # Копируем кастомные SSH конфиги
        for conf in "$SRV_SSH/sshd_config.d"/*.conf; do
            [[ -f "$conf" ]] || continue
            ln -sf "$conf" /etc/ssh/sshd_config.d/ 2>/dev/null || true
        done
        info "  SSH конфиги синхронизированы"
    fi
}

################################################################################
# ПРОВЕРКА ЗДОРОВЬЯ СИСТЕМЫ
################################################################################

health_check() {
    step "Проверка здоровья системы"
    
    local issues=0
    
    # Проверяем структуру директорий
    if [[ ! -d "$SRV_SYS" ]]; then
        error "Базовая директория /srv/sys/ не существует!"
        ((issues++))
    fi
    
    # Проверяем манифест
    if [[ ! -f "$MANIFEST" ]]; then
        warn "Манифест не найден"
        ((issues++))
    fi
    
    # Проверяем права
    if [[ ! -w "$SRV_SYS" ]]; then
        error "Нет прав на запись в /srv/sys/"
        ((issues++))
    fi
    
    # Проверяем iptables правила
    if [[ -f "$SRV_IPTABLES/v4/combined.v4" ]]; then
        info "  ✓ iptables IPv4 правила существуют"
    else
        warn "  ✗ iptables IPv4 правила не найдены"
        ((issues++))
    fi
    
    # Проверяем systemd units
    local units=(
        "iptables-restore.service"
        "ssh-session@.service"
    )
    
    for unit in "${units[@]}"; do
        if [[ -f "$SRV_SYSTEMD/system/$unit" ]]; then
            info "  ✓ $unit существует"
        else
            warn "  ✗ $unit не найден"
            ((issues++))
        fi
    done
    
    if [[ $issues -eq 0 ]]; then
        success "Система здорова, проблем не обнаружено"
        return 0
    else
        warn "Обнаружено проблем: $issues"
        return 1
    fi
}

################################################################################
# ОТЧЁТ О СИСТЕМЕ
################################################################################

generate_report() {
    step "Генерация отчёта о системе"
    
    local report="$SRV_SYS/system-report.txt"
    
    cat > "$report" <<REPORT_EOF
═══════════════════════════════════════════════════════════════════
SRV-SYS SYSTEM REPORT
Сгенерировано: $(date '+%Y-%m-%d %H:%M:%S')
═══════════════════════════════════════════════════════════════════

СИСТЕМА:
  Hostname: $(hostname)
  IP Address: $(hostname -I | awk '{print $1}')
  OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)
  Kernel: $(uname -r)
  Uptime: $(uptime -p)

СТРУКТУРА /srv/sys/:
$(tree -L 2 "$SRV_SYS" 2>/dev/null || find "$SRV_SYS" -maxdepth 2 -type d)

КОМПОНЕНТЫ:
$(if [[ -f "$MANIFEST" ]]; then
    echo "  Манифест: существует"
    if command -v jq &>/dev/null; then
        jq -r '.components | to_entries[] | "  \(.key): \(.value.enabled)"' "$MANIFEST" 2>/dev/null || echo "  (не удалось распарсить)"
    fi
else
    echo "  Манифест: не найден"
fi)

СЕРВИСЫ:
$(systemctl list-units --type=service --state=running | grep -E "nginx|mysql|postgresql|redis|mongodb" || echo "  Нет активных сервисов")

IPTABLES:
$(if [[ -f "$SRV_IPTABLES/v4/combined.v4" ]]; then
    echo "  IPv4 правил: $(grep -c '^-A' "$SRV_IPTABLES/v4/combined.v4" 2>/dev/null || echo 0)"
fi
if [[ -f "$SRV_IPTABLES/v6/combined.v6" ]]; then
    echo "  IPv6 правил: $(grep -c '^-A' "$SRV_IPTABLES/v6/combined.v6" 2>/dev/null || echo 0)"
fi)

SSH СЕССИИ:
  Активных: $(ls -1 "$SRV_SSH/ssh_session/active" 2>/dev/null | wc -l)
  Архивных: $(ls -1 "$SRV_SSH/ssh_session/archive" 2>/dev/null | wc -l)

РЕЗЕРВНЫЕ КОПИИ:
  Последняя: $(ls -1t "$SRV_BACKUPS"/*.tar.gz 2>/dev/null | head -1 | xargs basename 2>/dev/null || echo "нет")

ИСПОЛЬЗОВАНИЕ ДИСКА:
$(du -sh "$SRV_SYS" 2>/dev/null || echo "  Невозможно определить")

═══════════════════════════════════════════════════════════════════
REPORT_EOF
    
    info "Отчёт сохранён: $report"
    
    # Выводим отчёт
    cat "$report"
}

################################################################################
# ГЛАВНОЕ МЕНЮ
################################################################################

show_menu() {
    while true; do
        clear
        banner
        
        echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${CYAN}║                     ГЛАВНОЕ МЕНЮ                                  ║${NC}"
        echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo "  1. Полная инициализация системы"
        echo "  2. Обнаружение и интеграция сервисов"
        echo "  3. Автоконфигурация всех компонентов"
        echo "  4. Синхронизация конфигураций"
        echo "  5. Проверка здоровья системы"
        echo "  6. Генерация отчёта"
        echo "  7. Создание резервной копии"
        echo "  8. Просмотр манифеста"
        echo "  0. Выход"
        echo ""
        read -rp "Выберите действие: " choice
        
        case "$choice" in
            1)
                full_initialization
                read -rp "Нажмите Enter для продолжения..."
                ;;
            2)
                discover_services
                integrate_all_components
                read -rp "Нажмите Enter для продолжения..."
                ;;
            3)
                auto_configure_all
                read -rp "Нажмите Enter для продолжения..."
                ;;
            4)
                sync_all_components
                read -rp "Нажмите Enter для продолжения..."
                ;;
            5)
                health_check
                read -rp "Нажмите Enter для продолжения..."
                ;;
            6)
                generate_report
                read -rp "Нажмите Enter для продолжения..."
                ;;
            7)
                create_backup
                read -rp "Нажмите Enter для продолжения..."
                ;;
            8)
                view_manifest
                read -rp "Нажмите Enter для продолжения..."
                ;;
            0)
                success "Выход из интегратора"
                exit 0
                ;;
            *)
                error "Неверный выбор"
                sleep 1
                ;;
        esac
    done
}

################################################################################
# КОМПЛЕКСНЫЕ ОПЕРАЦИИ
################################################################################

full_initialization() {
    banner
    step "ПОЛНАЯ ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ"
    
    init_directory_structure
    create_manifest
    discover_services
    integrate_all_components
    auto_configure_all
    create_hooks
    sync_all_components
    health_check
    generate_report
    
    success "Полная инициализация завершена!"
}

integrate_all_components() {
    step "Интеграция всех компонентов"
    
    integrate_iptables
    integrate_ssh_sid
    integrate_win_config
    integrate_security
    
    success "Все компоненты интегрированы"
}

auto_configure_all() {
    step "Автоконфигурация всех сервисов"
    
    auto_configure_nginx
    auto_configure_mysql
    auto_configure_postgresql
    
    success "Автоконфигурация завершена"
}

create_backup() {
    step "Создание резервной копии /srv/sys/"
    
    local backup_name="srv-sys-backup-$(date +%Y%m%d_%H%M%S).tar.gz"
    local backup_path="$SRV_BACKUPS/$backup_name"
    
    tar -czf "$backup_path" \
        --exclude="$SRV_BACKUPS" \
        --exclude="$SRV_LOGS" \
        "$SRV_SYS" 2>/dev/null
    
    info "Резервная копия создана: $backup_path"
    info "Размер: $(du -h "$backup_path" | cut -f1)"
}

view_manifest() {
    if [[ -f "$MANIFEST" ]]; then
        if command -v jq &>/dev/null; then
            jq '.' "$MANIFEST" | less
        else
            cat "$MANIFEST" | less
        fi
    else
        error "Манифест не найден"
    fi
}

################################################################################
# ГЛАВНАЯ ФУНКЦИЯ
################################################################################

main() {
    # Проверка root
    if [[ $EUID -ne 0 ]]; then
        error "Требуются права root!"
        exit 1
    fi
    
    # Создаём базовую структуру если нужно
    [[ ! -d "$SRV_SYS" ]] && mkdir -p "$SRV_SYS"
    [[ ! -d "$SRV_LOGS" ]] && mkdir -p "$SRV_LOGS"
    
    # Проверяем аргументы командной строки
    case "${1:-}" in
        --init)
            full_initialization
            ;;
        --check)
            health_check
            ;;
        --report)
            generate_report
            ;;
        --backup)
            init_directory_structure
            create_backup
            ;;
        --sync)
            sync_all_components
            ;;
        *)
            show_menu
            ;;
    esac
}

main "$@"
