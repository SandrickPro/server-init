#!/bin/bash
################################################################################
# Module Uninstaller - Интеллектуальное удаление модулей
# Автор: Sandrick Tech
# Дата: 2024-12-09
# Описание: Полное удаление модулей со всеми зависимостями, конфигами и данными
################################################################################

set -euo pipefail

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Пути
BACKUP_DIR="/srv/sys/backups/uninstall"
LOG_FILE="/srv/sys/logs/uninstaller.log"
MANIFEST_DIR="/srv/sys/.manifests"

################################################################################
# УТИЛИТЫ
################################################################################

info() { echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"; }
step() { echo -e "${CYAN}[STEP]${NC} $1" | tee -a "$LOG_FILE"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"; }
error() { echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"; }

################################################################################
# МАНИФЕСТЫ МОДУЛЕЙ
################################################################################

# Структура манифеста (JSON):
# {
#   "name": "nginx",
#   "installed": "2024-12-09 15:30:00",
#   "packages": ["nginx", "nginx-extras", "php-fpm"],
#   "services": ["nginx", "php8.1-fpm"],
#   "directories": ["/srv/www", "/etc/nginx/sites-available"],
#   "config_files": ["/etc/nginx/nginx.conf"],
#   "ports": [80, 443],
#   "dependencies": []
# }

create_manifest() {
    local module_name="$1"
    shift
    local packages=("$@")
    
    mkdir -p "$MANIFEST_DIR"
    
    local manifest="$MANIFEST_DIR/${module_name}.json"
    
    cat > "$manifest" <<JSON
{
  "name": "$module_name",
  "installed": "$(date '+%Y-%m-%d %H:%M:%S')",
  "packages": $(printf '%s\n' "${packages[@]}" | jq -R . | jq -s .),
  "services": [],
  "directories": [],
  "config_files": [],
  "ports": [],
  "dependencies": []
}
JSON
    
    info "Манифест создан: $manifest"
}

update_manifest() {
    local module_name="$1"
    local key="$2"
    shift 2
    local values=("$@")
    
    local manifest="$MANIFEST_DIR/${module_name}.json"
    
    if [[ ! -f "$manifest" ]]; then
        error "Манифест не найден: $manifest"
        return 1
    fi
    
    # Обновляем JSON (добавляем значения в массив)
    local json_array=$(printf '%s\n' "${values[@]}" | jq -R . | jq -s .)
    jq ".$key += $json_array" "$manifest" > "${manifest}.tmp"
    mv "${manifest}.tmp" "$manifest"
}

################################################################################
# АНАЛИЗ ЗАВИСИМОСТЕЙ
################################################################################

get_package_dependencies() {
    local package="$1"
    
    # Получаем список зависимостей пакета
    apt-cache depends "$package" 2>/dev/null | grep "Depends:" | awk '{print $2}' || true
}

get_reverse_dependencies() {
    local package="$1"
    
    # Проверяем какие пакеты зависят от этого
    apt-cache rdepends "$package" 2>/dev/null | tail -n +3 || true
}

is_dependency_of_other() {
    local package="$1"
    
    # Проверяем используется ли пакет другими установленными пакетами
    local rdeps=$(get_reverse_dependencies "$package" | grep -v "^$package$" | wc -l)
    
    if (( rdeps > 0 )); then
        return 0  # Используется другими
    else
        return 1  # Не используется
    fi
}

################################################################################
# BACKUP ПЕРЕД УДАЛЕНИЕМ
################################################################################

backup_before_uninstall() {
    local module_name="$1"
    local manifest="$MANIFEST_DIR/${module_name}.json"
    
    if [[ ! -f "$manifest" ]]; then
        warn "Манифест не найден, пропускаем backup"
        return 0
    fi
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_path="$BACKUP_DIR/${module_name}_${timestamp}"
    
    mkdir -p "$backup_path"
    
    step "Создание backup перед удалением $module_name..."
    
    # Копируем манифест
    cp "$manifest" "$backup_path/manifest.json"
    
    # Копируем конфигурационные файлы
    local config_files=$(jq -r '.config_files[]' "$manifest" 2>/dev/null || true)
    if [[ -n "$config_files" ]]; then
        mkdir -p "$backup_path/configs"
        while IFS= read -r file; do
            if [[ -f "$file" ]]; then
                cp --parents "$file" "$backup_path/configs/" 2>/dev/null || true
            fi
        done <<< "$config_files"
    fi
    
    # Создаем список установленных пакетов
    dpkg --get-selections > "$backup_path/dpkg-selections.txt"
    
    info "✅ Backup создан: $backup_path"
    echo "$backup_path"
}

################################################################################
# УДАЛЕНИЕ МОДУЛЕЙ
################################################################################

uninstall_nginx() {
    step "Удаление Nginx..."
    
    # Останавливаем сервис
    systemctl stop nginx 2>/dev/null || true
    systemctl disable nginx 2>/dev/null || true
    
    # Удаляем пакеты
    apt-get purge -y nginx nginx-* php-fpm php8.* 2>/dev/null || true
    apt-get autoremove -y
    
    # Удаляем директории
    rm -rf /etc/nginx
    rm -rf /var/www/html
    rm -rf /srv/www
    rm -rf /var/log/nginx
    
    # Закрываем порты в iptables
    if command -v iptables &>/dev/null; then
        iptables -D INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null || true
        iptables -D INPUT -p tcp --dport 443 -j ACCEPT 2>/dev/null || true
        iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
    fi
    
    success "✅ Nginx удалён"
}

uninstall_mysql() {
    step "Удаление MySQL/MariaDB..."
    
    # Создаем backup баз данных
    if command -v mysqldump &>/dev/null; then
        local backup_sql="$BACKUP_DIR/mysql_$(date +%Y%m%d_%H%M%S).sql"
        mysqldump --all-databases > "$backup_sql" 2>/dev/null || true
        info "Backup БД сохранен: $backup_sql"
    fi
    
    systemctl stop mysql 2>/dev/null || true
    systemctl stop mariadb 2>/dev/null || true
    
    apt-get purge -y mysql-* mariadb-* 2>/dev/null || true
    apt-get autoremove -y
    
    rm -rf /etc/mysql
    rm -rf /var/lib/mysql
    rm -rf /var/log/mysql
    
    success "✅ MySQL удалён"
}

uninstall_postgresql() {
    step "Удаление PostgreSQL..."
    
    systemctl stop postgresql 2>/dev/null || true
    
    apt-get purge -y postgresql postgresql-* 2>/dev/null || true
    apt-get autoremove -y
    
    rm -rf /etc/postgresql
    rm -rf /var/lib/postgresql
    
    success "✅ PostgreSQL удалён"
}

uninstall_docker() {
    step "Удаление Docker..."
    
    # Останавливаем все контейнеры
    docker stop $(docker ps -aq) 2>/dev/null || true
    docker rm $(docker ps -aq) 2>/dev/null || true
    
    systemctl stop docker 2>/dev/null || true
    
    apt-get purge -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    apt-get autoremove -y
    
    rm -rf /var/lib/docker
    rm -rf /etc/docker
    
    success "✅ Docker удалён"
}

uninstall_python_env() {
    step "Удаление окружения Python..."
    
    # Удаляем глобальные pip пакеты (осторожно!)
    pip3 freeze > /tmp/pip_packages.txt 2>/dev/null || true
    
    rm -rf /srv/dev/examples/python
    rm -rf ~/.local/lib/python*
    
    # Удаляем только пользовательские пакеты
    # apt-get remove -y python3-pip (оставляем Python3, удаляем только pip)
    
    success "✅ Python окружение очищено"
}

uninstall_c_env() {
    step "Удаление окружения C/C++..."
    
    apt-get remove -y build-essential gcc g++ make cmake gdb valgrind 2>/dev/null || true
    apt-get autoremove -y
    
    rm -rf /srv/dev/examples/c
    
    success "✅ C/C++ окружение удалено"
}

uninstall_dns_server() {
    step "Удаление DNS сервера..."
    
    systemctl stop dnsmasq 2>/dev/null || true
    systemctl disable dnsmasq 2>/dev/null || true
    
    apt-get purge -y dnsmasq 2>/dev/null || true
    apt-get autoremove -y
    
    rm -rf /etc/dnsmasq.d
    rm -f /etc/dnsmasq.conf
    
    # Восстанавливаем systemd-resolved если был отключен
    if ! systemctl is-active --quiet systemd-resolved; then
        systemctl enable systemd-resolved
        systemctl start systemd-resolved
        ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
    fi
    
    success "✅ DNS сервер удалён"
}

################################################################################
# ИНТЕЛЛЕКТУАЛЬНОЕ УДАЛЕНИЕ
################################################################################

smart_uninstall() {
    local module_name="$1"
    
    dialog --title "Удаление модуля" \
        --yesno "Вы уверены, что хотите удалить '$module_name'?\n\nБудет удалено:\n• Пакеты и зависимости\n• Конфигурационные файлы\n• Данные и логи\n\nBackup будет создан автоматически." 14 60 || return
    
    # Создаем backup
    local backup_path=$(backup_before_uninstall "$module_name")
    
    # Удаляем модуль
    case "$module_name" in
        nginx|web-server)
            uninstall_nginx
            ;;
        mysql|mariadb)
            uninstall_mysql
            ;;
        postgresql)
            uninstall_postgresql
            ;;
        docker)
            uninstall_docker
            ;;
        python-env)
            uninstall_python_env
            ;;
        c-env)
            uninstall_c_env
            ;;
        dns-server)
            uninstall_dns_server
            ;;
        *)
            error "Неизвестный модуль: $module_name"
            return 1
            ;;
    esac
    
    # Удаляем манифест
    rm -f "$MANIFEST_DIR/${module_name}.json"
    
    dialog --msgbox "✅ Модуль '$module_name' успешно удалён!\n\nBackup сохранен в:\n$backup_path" 10 60
}

################################################################################
# МЕНЮ
################################################################################

uninstaller_menu() {
    mkdir -p "$BACKUP_DIR" "$MANIFEST_DIR" "$(dirname $LOG_FILE)"
    
    while true; do
        local choice=$(dialog --clear \
            --backtitle "Module Uninstaller" \
            --title "Удаление модулей" \
            --menu "Выберите модуль для удаления:" \
            20 70 12 \
            1 "🌐 Nginx + PHP + Web" \
            2 "🗄  MySQL/MariaDB" \
            3 "🐘 PostgreSQL" \
            4 "🐳 Docker" \
            5 "🐍 Python окружение" \
            6 "🔧 C/C++ окружение" \
            7 "🌐 DNS сервер (dnsmasq)" \
            8 "📦 Полная очистка (все модули)" \
            9 "📋 Показать установленные модули" \
            10 "♻️  Восстановить из backup" \
            0 "◀ Назад" \
            3>&1 1>&2 2>&3)
        
        case $choice in
            1) smart_uninstall "nginx" ;;
            2) smart_uninstall "mysql" ;;
            3) smart_uninstall "postgresql" ;;
            4) smart_uninstall "docker" ;;
            5) smart_uninstall "python-env" ;;
            6) smart_uninstall "c-env" ;;
            7) smart_uninstall "dns-server" ;;
            8)
                dialog --yesno "⚠️  ВНИМАНИЕ!\n\nЭто удалит ВСЕ модули!\nПродолжить?" 10 50 || continue
                smart_uninstall "nginx"
                smart_uninstall "mysql"
                smart_uninstall "postgresql"
                smart_uninstall "docker"
                smart_uninstall "python-env"
                smart_uninstall "c-env"
                smart_uninstall "dns-server"
                ;;
            9)
                local installed=""
                for manifest in "$MANIFEST_DIR"/*.json; do
                    if [[ -f "$manifest" ]]; then
                        installed+="$(basename $manifest .json)\n"
                    fi
                done
                dialog --msgbox "Установленные модули:\n\n${installed:-Нет установленных модулей}" 15 50
                ;;
            10)
                # TODO: Восстановление из backup
                dialog --msgbox "Функция в разработке" 6 30
                ;;
            0|"") return ;;
        esac
    done
}

################################################################################
# ТОЧКА ВХОДА
################################################################################

main() {
    if [[ $EUID -ne 0 ]]; then
        error "Требуются права root"
        exit 1
    fi
    
    # Проверяем наличие jq
    if ! command -v jq &>/dev/null; then
        apt-get install -y jq
    fi
    
    uninstaller_menu
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
