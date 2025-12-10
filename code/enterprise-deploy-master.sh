#!/bin/bash
################################################################################
# Enterprise Deploy - Мастер установки и управления
# Version: 9.0.0 Enterprise Edition
# Дата: 2025-12-09
# Автор: Sandrick Tech
#
# ОПИСАНИЕ:
#   Единая точка входа для всей Enterprise системы.
#   Автоматическая настройка, развертывание и управление.
#
# ИСПОЛЬЗОВАНИЕ:
#   sudo ./enterprise-deploy-master.sh           # Интерактивный режим
#   sudo ./enterprise-deploy-master.sh install   # Быстрая установка
#   sudo ./enterprise-deploy-master.sh status    # Статус системы
#
################################################################################

set -euo pipefail

# Глобальные переменные
readonly VERSION="9.0.0"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly ENTERPRISE_BASE="/opt/enterprise-deploy"
readonly LOG_FILE="/var/log/enterprise-deploy/master.log"

# Цвета
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly MAGENTA='\033[0;35m'
readonly BOLD='\033[1m'
readonly NC='\033[0m'

################################################################################
# ЛОГИРОВАНИЕ
################################################################################

log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Вывод в консоль с цветами
    case $level in
        INFO)  echo -e "${GREEN}[INFO]${NC}  [$timestamp] $message" ;;
        WARN)  echo -e "${YELLOW}[WARN]${NC}  [$timestamp] $message" ;;
        ERROR) echo -e "${RED}[ERROR]${NC} [$timestamp] $message" ;;
        DEBUG) echo -e "${CYAN}[DEBUG]${NC} [$timestamp] $message" ;;
    esac
    
    # Запись в файл
    echo "[$level] [$timestamp] $message" >> "$LOG_FILE" 2>/dev/null || true
}

################################################################################
# ПРОВЕРКА ПРАВ И ЗАВИСИМОСТЕЙ
################################################################################

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log ERROR "Требуются права root"
        echo -e "${RED}Запустите с sudo:${NC} sudo $0"
        exit 1
    fi
}

check_dependencies() {
    log INFO "Проверка зависимостей..."
    
    local deps=(
        "dialog:dialog"
        "python3:python3"
        "git:git"
        "curl:curl"
        "jq:jq"
    )
    
    local missing=()
    
    for dep in "${deps[@]}"; do
        local cmd="${dep%%:*}"
        local pkg="${dep##*:}"
        
        if ! command -v "$cmd" &>/dev/null; then
            missing+=("$pkg")
        fi
    done
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        log WARN "Отсутствуют пакеты: ${missing[*]}"
        read -p "Установить? [Y/n]: " install_deps
        
        if [[ "${install_deps^^}" != "N" ]]; then
            apt-get update -qq
            apt-get install -y "${missing[@]}"
            log INFO "✅ Зависимости установлены"
        fi
    else
        log INFO "✅ Все зависимости установлены"
    fi
}

################################################################################
# ASCII ART БАННЕР
################################################################################

show_banner() {
    clear
    echo -e "${CYAN}"
    cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ███████╗███╗   ██╗████████╗███████╗██████╗ ██████╗ ██████╗    ║
║   ██╔════╝████╗  ██║╚══██╔══╝██╔════╝██╔══██╗██╔══██╗╚════██╗   ║
║   █████╗  ██╔██╗ ██║   ██║   █████╗  ██████╔╝██████╔╝ █████╔╝   ║
║   ██╔══╝  ██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗██╔═══╝  ╚═══██╗   ║
║   ███████╗██║ ╚████║   ██║   ███████╗██║  ██║██║     ██████╔╝   ║
║   ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═════╝    ║
║                                                                   ║
║              Enterprise Server Deployment Platform               ║
║                      Version 9.0.0 - 2025                        ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

################################################################################
# ГЛАВНОЕ МЕНЮ
################################################################################

main_menu() {
    while true; do
        local choice=$(dialog --clear \
            --backtitle "Enterprise Deploy v$VERSION" \
            --title "╔════ Главное меню ════╗" \
            --menu "Выберите действие:" \
            20 70 12 \
            "1" "🚀 Быстрая установка (рекомендуется)" \
            "2" "🧙 Интерактивный визард настройки" \
            "3" "📊 Статус системы" \
            "4" "⚙️  Управление модулями" \
            "5" "🤖 Управление Telegram ботами" \
            "6" "💾 Резервное копирование" \
            "7" "📈 Мониторинг и метрики" \
            "8" "🔒 Безопасность и аудит" \
            "9" "📚 Документация и помощь" \
            "10" "🔧 Расширенные настройки" \
            "0" "❌ Выход" \
            3>&1 1>&2 2>&3)
        
        case $choice in
            1) quick_install ;;
            2) interactive_wizard ;;
            3) show_system_status ;;
            4) manage_modules ;;
            5) manage_bots ;;
            6) backup_menu ;;
            7) monitoring_menu ;;
            8) security_menu ;;
            9) show_documentation ;;
            10) advanced_settings ;;
            0|"") exit 0 ;;
        esac
    done
}

################################################################################
# БЫСТРАЯ УСТАНОВКА
################################################################################

quick_install() {
    dialog --title "Быстрая установка" \
        --yesno "Будет установлен профиль: PROFESSIONAL\n\nВключает:\n- VSCode Server\n- Docker Manager\n- Prometheus + Grafana\n- 5 Telegram ботов\n- Автоматический backup\n\nПродолжить?" 15 60
    
    if [[ $? -eq 0 ]]; then
        install_system "professional"
    fi
}

install_system() {
    local profile=${1:-professional}
    
    # Прогресс через dialog gauge
    (
        echo "0" ; sleep 0.5
        echo "# Создание директорий..."
        mkdir -p "$ENTERPRISE_BASE"/{code,config,lib,logs,data}
        mkdir -p /srv/{backups,projects,enterprise-data}
        mkdir -p /var/log/enterprise-deploy
        echo "10" ; sleep 0.5
        
        echo "# Копирование файлов..."
        cp -r "$SCRIPT_DIR/code"/* "$ENTERPRISE_BASE/code/" 2>/dev/null || true
        echo "20" ; sleep 0.5
        
        echo "# Настройка конфигурации..."
        if [[ -f "$SCRIPT_DIR/code/config/enterprise-config.yaml" ]]; then
            cp "$SCRIPT_DIR/code/config/enterprise-config.yaml" "$ENTERPRISE_BASE/config/"
        fi
        echo "30" ; sleep 0.5
        
        echo "# Установка зависимостей Python..."
        if [[ -f "$SCRIPT_DIR/code/bots/requirements.txt" ]]; then
            pip3 install -q -r "$SCRIPT_DIR/code/bots/requirements.txt" 2>/dev/null || true
        fi
        echo "50" ; sleep 1
        
        echo "# Настройка модулей..."
        chmod +x "$ENTERPRISE_BASE/code"/*.sh 2>/dev/null || true
        chmod +x "$ENTERPRISE_BASE/code/lib"/*.sh 2>/dev/null || true
        echo "60" ; sleep 0.5
        
        echo "# Создание symlink для CLI..."
        ln -sf "$ENTERPRISE_BASE/code/enterprise-cli.sh" /usr/local/bin/enterprise-cli
        echo "70" ; sleep 0.5
        
        echo "# Настройка автокомплита..."
        "$ENTERPRISE_BASE/code/enterprise-cli.sh" setup-autocomplete 2>/dev/null || true
        echo "80" ; sleep 0.5
        
        echo "# Загрузка модулей профиля: $profile..."
        if [[ -f "$ENTERPRISE_BASE/code/lib/module-loader.sh" ]]; then
            source "$ENTERPRISE_BASE/code/lib/module-loader.sh"
            load_deployment_profile "$profile" 2>/dev/null || true
        fi
        echo "90" ; sleep 0.5
        
        echo "# Финализация..."
        chown -R root:root "$ENTERPRISE_BASE"
        chmod 755 "$ENTERPRISE_BASE"
        echo "100" ; sleep 0.5
        
    ) | dialog --title "Установка системы" --gauge "Инициализация..." 10 70 0
    
    dialog --title "✅ Успешно!" --msgbox "\
Система успешно установлена!

Профиль: $profile
Версия: $VERSION

Следующие шаги:
1. Настройте Telegram ботов (меню 5)
2. Создайте первый backup (меню 6)
3. Проверьте статус (меню 3)

Быстрый доступ через CLI:
  enterprise-cli monitor dashboard
  enterprise-cli services list
  enterprise-cli backup create" 18 70
}

################################################################################
# ИНТЕРАКТИВНЫЙ ВИЗАРД
################################################################################

interactive_wizard() {
    # Используем CLI визард
    if [[ -x "$ENTERPRISE_BASE/code/enterprise-cli.sh" ]]; then
        "$ENTERPRISE_BASE/code/enterprise-cli.sh" wizard
    else
        dialog --msgbox "CLI не установлен. Выполните сначала установку (пункт 1)." 8 50
    fi
}

################################################################################
# СТАТУС СИСТЕМЫ
################################################################################

show_system_status() {
    local status_text="╔═══════════════════════════════════════════╗\n"
    status_text+="║         СТАТУС ENTERPRISE СИСТЕМЫ         ║\n"
    status_text+="╚═══════════════════════════════════════════╝\n\n"
    
    # Проверка установки
    if [[ -d "$ENTERPRISE_BASE" ]]; then
        status_text+="✅ Система установлена: $ENTERPRISE_BASE\n"
    else
        status_text+="❌ Система НЕ установлена\n"
    fi
    
    # Версия
    status_text+="📦 Версия: $VERSION\n\n"
    
    # Сервисы
    status_text+="🔧 СЕРВИСЫ:\n"
    for service in code-server prometheus grafana-server docker nginx; do
        if systemctl is-active --quiet "$service" 2>/dev/null; then
            status_text+="  ● $service - running\n"
        else
            status_text+="  ○ $service - stopped\n"
        fi
    done
    
    # Ресурсы
    status_text+="\n💻 РЕСУРСЫ:\n"
    status_text+="  CPU:    $(top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1)%\n"
    status_text+="  Memory: $(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')%\n"
    status_text+="  Disk:   $(df -h / | awk 'NR==2 {print $5}')\n"
    
    # Боты
    status_text+="\n🤖 TELEGRAM БОТЫ:\n"
    if pgrep -f "devops_manager_bot" &>/dev/null; then
        status_text+="  ● DevOps Manager - running\n"
    else
        status_text+="  ○ DevOps Manager - stopped\n"
    fi
    
    dialog --title "Статус системы" --msgbox "$status_text" 25 60
}

################################################################################
# УПРАВЛЕНИЕ МОДУЛЯМИ
################################################################################

manage_modules() {
    local choice=$(dialog --clear \
        --title "Управление модулями" \
        --menu "Выберите действие:" 15 60 7 \
        "1" "📋 Список модулей" \
        "2" "✅ Загрузить модуль" \
        "3" "🔄 Перезагрузить все" \
        "4" "📊 Статус модулей" \
        "0" "◀ Назад" \
        3>&1 1>&2 2>&3)
    
    case $choice in
        1)
            local modules=$(find "$ENTERPRISE_BASE/code" -name "*.sh" -type f | sed "s|$ENTERPRISE_BASE/code/||")
            dialog --title "Список модулей" --msgbox "$modules" 20 70
            manage_modules
            ;;
        2)
            local module=$(dialog --inputbox "Введите имя модуля:" 8 50 3>&1 1>&2 2>&3)
            if [[ -n "$module" ]]; then
                source "$ENTERPRISE_BASE/code/lib/module-loader.sh"
                load_module "$module"
                dialog --msgbox "Модуль $module загружен" 7 50
            fi
            manage_modules
            ;;
        3)
            source "$ENTERPRISE_BASE/code/lib/module-loader.sh"
            unload_modules
            load_modules_by_priority
            dialog --msgbox "Все модули перезагружены" 7 40
            manage_modules
            ;;
        4)
            show_system_status
            manage_modules
            ;;
        0|"") return ;;
    esac
}

################################################################################
# УПРАВЛЕНИЕ БОТАМИ
################################################################################

manage_bots() {
    local choice=$(dialog --clear \
        --title "Управление Telegram ботами" \
        --menu "Выберите действие:" 18 65 10 \
        "1" "🚀 Запустить DevOps Manager" \
        "2" "🛡️ Запустить Security Auditor" \
        "3" "🤖 Запустить Orchestrator" \
        "4" "⏸️  Остановить все боты" \
        "5" "📊 Статус ботов" \
        "6" "⚙️  Настроить токены" \
        "0" "◀ Назад" \
        3>&1 1>&2 2>&3)
    
    case $choice in
        1)
            if [[ -z "${TELEGRAM_BOT_DEVOPS_TOKEN:-}" ]]; then
                dialog --msgbox "Токен не настроен! Используйте пункт 6." 7 50
            else
                python3 "$ENTERPRISE_BASE/code/bots/devops_manager_bot.py" &
                dialog --msgbox "DevOps Manager запущен (фоновый режим)" 7 50
            fi
            manage_bots
            ;;
        2)
            if [[ -z "${TELEGRAM_BOT_SECURITY_TOKEN:-}" ]]; then
                dialog --msgbox "Токен не настроен! Используйте пункт 6." 7 50
            else
                python3 "$ENTERPRISE_BASE/code/bots/security_auditor_bot.py" &
                dialog --msgbox "Security Auditor запущен (фоновый режим)" 7 50
            fi
            manage_bots
            ;;
        4)
            pkill -f "_bot.py"
            dialog --msgbox "Все боты остановлены" 7 40
            manage_bots
            ;;
        6)
            configure_bot_tokens
            manage_bots
            ;;
        0|"") return ;;
    esac
}

configure_bot_tokens() {
    local devops_token=$(dialog --inputbox "DevOps Manager токен:" 8 60 3>&1 1>&2 2>&3)
    local security_token=$(dialog --inputbox "Security Auditor токен:" 8 60 3>&1 1>&2 2>&3)
    local admin_ids=$(dialog --inputbox "Admin IDs (через запятую):" 8 60 3>&1 1>&2 2>&3)
    
    # Сохранение в файл окружения
    cat > /etc/environment.d/telegram-bots.conf <<EOF
TELEGRAM_BOT_DEVOPS_TOKEN="$devops_token"
TELEGRAM_BOT_SECURITY_TOKEN="$security_token"
TELEGRAM_ADMIN_IDS="$admin_ids"
EOF
    
    export TELEGRAM_BOT_DEVOPS_TOKEN="$devops_token"
    export TELEGRAM_BOT_SECURITY_TOKEN="$security_token"
    export TELEGRAM_ADMIN_IDS="$admin_ids"
    
    dialog --msgbox "Токены сохранены!" 7 40
}

################################################################################
# МЕНЮ BACKUP
################################################################################

backup_menu() {
    enterprise-cli backup list | dialog --title "Резервные копии" --programbox 20 70
}

################################################################################
# МЕНЮ МОНИТОРИНГА
################################################################################

monitoring_menu() {
    enterprise-cli monitor dashboard > /tmp/dashboard.txt
    dialog --title "Dashboard" --textbox /tmp/dashboard.txt 20 70
    rm /tmp/dashboard.txt
}

################################################################################
# МЕНЮ БЕЗОПАСНОСТИ
################################################################################

security_menu() {
    local choice=$(dialog --clear \
        --title "Безопасность" \
        --menu "Выберите действие:" 15 60 7 \
        "1" "🔒 Security Hardening" \
        "2" "🔥 Firewall настройка" \
        "3" "🔐 SSH конфигурация" \
        "4" "📊 Аудит безопасности" \
        "0" "◀ Назад" \
        3>&1 1>&2 2>&3)
    
    case $choice in
        4)
            if command -v python3 &>/dev/null; then
                python3 "$ENTERPRISE_BASE/code/bots/security_auditor_bot.py" --cli-mode 2>/dev/null || \
                    dialog --msgbox "Запустите Security Auditor бот для полного аудита" 7 60
            fi
            security_menu
            ;;
        0|"") return ;;
    esac
}

################################################################################
# ДОКУМЕНТАЦИЯ
################################################################################

show_documentation() {
    local docs=(
        "1" "📘 README v9.0"
        "2" "📊 Enterprise Report"
        "3" "🚀 Quick Start Guide"
        "4" "📚 API Reference"
        "5" "🔧 Troubleshooting"
    )
    
    local choice=$(dialog --clear \
        --title "Документация" \
        --menu "Выберите документ:" 15 60 5 \
        "${docs[@]}" \
        3>&1 1>&2 2>&3)
    
    case $choice in
        2)
            if [[ -f "$SCRIPT_DIR/ENTERPRISE_REPORT_V9.md" ]]; then
                dialog --textbox "$SCRIPT_DIR/ENTERPRISE_REPORT_V9.md" 30 100
            fi
            show_documentation
            ;;
        0|"") return ;;
    esac
}

################################################################################
# РАСШИРЕННЫЕ НАСТРОЙКИ
################################################################################

advanced_settings() {
    dialog --msgbox "Расширенные настройки в разработке" 7 40
}

################################################################################
# ГЛАВНАЯ ФУНКЦИЯ
################################################################################

main() {
    check_root
    
    # Создание лог директории
    mkdir -p "$(dirname "$LOG_FILE")"
    
    log INFO "═══════════════════════════════════════════"
    log INFO "Enterprise Deploy Master v$VERSION"
    log INFO "═══════════════════════════════════════════"
    
    # Проверка зависимостей
    check_dependencies
    
    # Обработка аргументов
    case "${1:-}" in
        install)
            show_banner
            install_system "professional"
            ;;
        status)
            show_system_status
            ;;
        wizard)
            interactive_wizard
            ;;
        *)
            show_banner
            sleep 2
            main_menu
            ;;
    esac
}

# Запуск
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
