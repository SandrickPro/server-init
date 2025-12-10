#!/bin/bash
################################################################################
# System Update Manager
# Автор: Sandrick Tech
# Дата: 2024-12-09
# Описание: Безопасное обновление системы и ядра с резервным копированием
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

# Глобальные переменные
BACKUP_DIR="/srv/sys/backups"
LOG_FILE="/srv/sys/logs/system-update.log"
UPDATE_STATE="/srv/sys/.update_state"

################################################################################
# УТИЛИТЫ
################################################################################

info() { 
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

warn() { 
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

error() { 
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

step() { 
    echo -e "${CYAN}[STEP]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

################################################################################
# ПРОВЕРКИ СОСТОЯНИЯ
################################################################################

check_system_ready() {
    step "Проверка готовности системы к обновлению..."
    
    # Проверяем свободное место
    local free_space=$(df / | tail -1 | awk '{print $4}')
    if (( free_space < 1048576 )); then # < 1GB
        error "Недостаточно свободного места! Требуется минимум 1GB"
        return 1
    fi
    
    # Проверяем наличие активных пользователей
    local active_users=$(who | wc -l)
    if (( active_users > 1 )); then
        warn "Обнаружено $active_users активных пользователей"
        dialog --yesno "Продолжить обновление?" 8 50 || return 1
    fi
    
    # Проверяем наличие запущенных критичных процессов
    if pgrep -x "mysqld" > /dev/null; then
        warn "MySQL запущен. Рекомендуется сделать дамп базы данных"
    fi
    
    info "✅ Система готова к обновлению"
    return 0
}

get_system_info() {
    cat <<INFO
╔════════════════════════════════════════════════════════════╗
║               ИНФОРМАЦИЯ О СИСТЕМЕ                         ║
╠════════════════════════════════════════════════════════════╣
║ OS: $(lsb_release -d | cut -f2-)
║ Kernel: $(uname -r)
║ Uptime: $(uptime -p)
║ CPU: $(lscpu | grep 'Model name' | cut -d':' -f2 | xargs)
║ Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')
║ Disk: $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 ")"}')
║ Updates Available: $(apt list --upgradable 2>/dev/null | grep -c upgradable || echo "0")
╚════════════════════════════════════════════════════════════╝
INFO
}

################################################################################
# РЕЗЕРВНОЕ КОПИРОВАНИЕ
################################################################################

create_system_snapshot() {
    step "Создание снимка системы перед обновлением..."
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local snapshot_dir="$BACKUP_DIR/snapshot_$timestamp"
    
    mkdir -p "$snapshot_dir"
    
    # Сохраняем список пакетов
    dpkg --get-selections > "$snapshot_dir/packages.list"
    apt-mark showauto > "$snapshot_dir/packages-auto.list"
    
    # Сохраняем конфигурации
    tar -czf "$snapshot_dir/etc-configs.tar.gz" \
        /etc/apt/sources.list.d/ \
        /etc/ssh/ \
        /etc/nginx/ 2>/dev/null || true
    
    # Сохраняем информацию о ядре
    uname -a > "$snapshot_dir/kernel-info.txt"
    
    # Сохраняем состояние обновления
    cat > "$snapshot_dir/update-state.json" <<JSON
{
    "timestamp": "$timestamp",
    "kernel": "$(uname -r)",
    "os": "$(lsb_release -d | cut -f2-)",
    "packages_count": $(dpkg --get-selections | wc -l)
}
JSON
    
    echo "$snapshot_dir" > "$UPDATE_STATE"
    
    success "✅ Снимок создан: $snapshot_dir"
    return 0
}

restore_from_snapshot() {
    local snapshot_dir="${1:-$(cat $UPDATE_STATE 2>/dev/null)}"
    
    if [[ ! -d "$snapshot_dir" ]]; then
        error "Снимок не найден: $snapshot_dir"
        return 1
    fi
    
    step "Восстановление из снимка: $snapshot_dir"
    
    # Восстанавливаем список пакетов
    if [[ -f "$snapshot_dir/packages.list" ]]; then
        dpkg --set-selections < "$snapshot_dir/packages.list"
        apt-get dselect-upgrade -y
    fi
    
    # Восстанавливаем конфигурации
    if [[ -f "$snapshot_dir/etc-configs.tar.gz" ]]; then
        tar -xzf "$snapshot_dir/etc-configs.tar.gz" -C /
    fi
    
    success "✅ Восстановление завершено"
    return 0
}

################################################################################
# ОБНОВЛЕНИЕ ПАКЕТОВ
################################################################################

update_package_lists() {
    step "Обновление списков пакетов..."
    
    (
        echo "10" ; sleep 1
        apt-get update -qq 2>&1
        echo "100"
    ) | dialog --gauge "Обновление списков пакетов..." 8 50 0
    
    local upgradable=$(apt list --upgradable 2>/dev/null | grep -c upgradable || echo "0")
    
    info "Доступно обновлений: $upgradable"
    return 0
}

upgrade_packages() {
    step "Обновление пакетов..."
    
    local packages=$(apt list --upgradable 2>/dev/null | grep -c upgradable || echo "0")
    
    if (( packages == 0 )); then
        dialog --msgbox "Все пакеты уже обновлены" 8 40
        return 0
    fi
    
    # Показываем список обновлений
    apt list --upgradable 2>/dev/null | tail -n +2 > /tmp/upgradable.txt
    
    dialog --title "Доступные обновления ($packages)" \
        --textbox /tmp/upgradable.txt 20 70
    
    dialog --yesno "Начать обновление $packages пакетов?" 8 50 || return 0
    
    # Обновляем с прогресс-баром
    (
        apt-get upgrade -y 2>&1 | while read line; do
            echo "$line"
        done
    ) | dialog --programbox "Обновление пакетов..." 20 70
    
    success "✅ Пакеты обновлены"
    return 0
}

dist_upgrade() {
    step "Полное обновление системы (dist-upgrade)..."
    
    dialog --yesno "Выполнить dist-upgrade?\n\nЭто может изменить зависимости пакетов" 10 60 || return 0
    
    (
        apt-get dist-upgrade -y 2>&1 | while read line; do
            echo "$line"
        done
    ) | dialog --programbox "Обновление системы..." 20 70
    
    success "✅ Система обновлена"
    return 0
}

################################################################################
# ОБНОВЛЕНИЕ ЯДРА
################################################################################

check_kernel_updates() {
    step "Проверка обновлений ядра..."
    
    local current_kernel=$(uname -r)
    local latest_kernel=$(apt-cache policy linux-image-generic | grep Candidate | awk '{print $2}')
    
    info "Текущее ядро: $current_kernel"
    info "Доступное ядро: $latest_kernel"
    
    if dpkg --compare-versions "$latest_kernel" gt "$current_kernel"; then
        return 0 # Есть обновление
    else
        return 1 # Обновлений нет
    fi
}

upgrade_kernel() {
    step "Обновление ядра Linux..."
    
    if ! check_kernel_updates; then
        dialog --msgbox "Ядро уже обновлено до последней версии" 8 50
        return 0
    fi
    
    local current=$(uname -r)
    
    dialog --yesno "Обновить ядро?\n\nТекущее: $current\n\nПосле обновления потребуется перезагрузка" 12 60 || return 0
    
    (
        echo "20" ; sleep 1
        apt-get install -y linux-generic linux-headers-generic 2>&1
        echo "100"
    ) | dialog --gauge "Установка нового ядра..." 8 50 0
    
    success "✅ Ядро обновлено. Требуется перезагрузка"
    
    dialog --yesno "Перезагрузить систему сейчас?" 8 40 && reboot || return 0
}

list_installed_kernels() {
    step "Список установленных ядер..."
    
    dpkg --list | grep linux-image > /tmp/kernels.txt
    
    dialog --title "Установленные ядра" \
        --textbox /tmp/kernels.txt 20 70
}

remove_old_kernels() {
    step "Удаление старых ядер..."
    
    local current_kernel=$(uname -r)
    
    dialog --msgbox "Текущее ядро: $current_kernel\n\nБудут удалены только старые ядра" 10 50
    
    apt-get autoremove --purge -y 2>&1 | dialog --programbox "Очистка старых ядер..." 20 70
    
    success "✅ Старые ядра удалены"
}

################################################################################
# ОЧИСТКА СИСТЕМЫ
################################################################################

cleanup_system() {
    step "Очистка системы..."
    
    local tasks=(
        "apt-get autoremove -y"
        "apt-get autoclean"
        "apt-get clean"
        "journalctl --vacuum-time=7d"
    )
    
    local total=${#tasks[@]}
    local current=0
    
    (
        for task in "${tasks[@]}"; do
            current=$((current + 1))
            percent=$((current * 100 / total))
            echo "$percent"
            echo "# Выполнение: $task"
            eval "$task" 2>&1 | tail -5
            sleep 1
        done
    ) | dialog --gauge "Очистка системы..." 10 70 0
    
    # Показываем освобождённое место
    local freed=$(du -sh /var/cache/apt/archives/ 2>/dev/null | awk '{print $1}')
    
    success "✅ Очистка завершена (освобождено: $freed)"
}

################################################################################
# МЕНЮ
################################################################################

update_menu() {
    while true; do
        local choice=$(dialog --clear \
            --backtitle "System Update Manager" \
            --title "Управление обновлениями" \
            --menu "Выберите действие:" \
            20 70 12 \
            1 "📊 Информация о системе" \
            2 "🔄 Обновить списки пакетов" \
            3 "⬆️  Обновить пакеты (upgrade)" \
            4 "⬆️⬆️ Полное обновление (dist-upgrade)" \
            5 "🐧 Обновить ядро Linux" \
            6 "🗑️  Удалить старые ядра" \
            7 "📋 Список установленных ядер" \
            8 "💾 Создать снимок системы" \
            9 "♻️  Восстановить из снимка" \
            10 "🧹 Очистка системы" \
            11 "🚀 Полное обновление (всё сразу)" \
            0 "◀ Назад" \
            3>&1 1>&2 2>&3)
        
        case $choice in
            1) 
                get_system_info > /tmp/sysinfo.txt
                dialog --textbox /tmp/sysinfo.txt 20 70
                ;;
            2) update_package_lists ;;
            3) upgrade_packages ;;
            4) dist_upgrade ;;
            5) upgrade_kernel ;;
            6) remove_old_kernels ;;
            7) list_installed_kernels ;;
            8) create_system_snapshot ;;
            9) 
                local snapshots=($(ls -1dt $BACKUP_DIR/snapshot_* 2>/dev/null | head -5))
                if (( ${#snapshots[@]} == 0 )); then
                    dialog --msgbox "Снимки не найдены" 8 40
                else
                    local menu_items=()
                    for snap in "${snapshots[@]}"; do
                        menu_items+=("$(basename $snap)" "")
                    done
                    local selected=$(dialog --menu "Выберите снимок:" 15 60 5 "${menu_items[@]}" 3>&1 1>&2 2>&3)
                    [[ -n "$selected" ]] && restore_from_snapshot "$BACKUP_DIR/$selected"
                fi
                ;;
            10) cleanup_system ;;
            11)
                if ! check_system_ready; then
                    dialog --msgbox "Система не готова к обновлению" 8 40
                    continue
                fi
                
                dialog --yesno "Выполнить полное обновление?\n\n• Создать снимок\n• Обновить списки\n• Обновить пакеты\n• Обновить ядро\n• Очистить систему" 14 60 || continue
                
                create_system_snapshot
                update_package_lists
                upgrade_packages
                dist_upgrade
                upgrade_kernel
                cleanup_system
                
                dialog --msgbox "✅ Полное обновление завершено!" 8 40
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
    
    # Создаём директории
    mkdir -p "$BACKUP_DIR" "$(dirname $LOG_FILE)"
    
    # Запускаем меню
    update_menu
}

# Если запущен напрямую
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
