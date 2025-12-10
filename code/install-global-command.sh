#!/bin/bash
################################################################################
# System Config Global Command Installer
# Автор: Sandrick Tech
# Дата: 2024-12-09
# Описание: Установка глобальной команды system-config
################################################################################

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
step() { echo -e "${CYAN}[STEP]${NC} $1"; }

################################################################################
# УСТАНОВКА
################################################################################

install_system_config() {
    step "Установка глобальной команды system-config..."
    
    # Определяем путь к главному скрипту
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local main_script="$script_dir/server-deploy-v5-enhanced.sh"
    
    if [[ ! -f "$main_script" ]]; then
        error "Главный скрипт не найден: $main_script"
        return 1
    fi
    
    # Делаем скрипт исполняемым
    chmod +x "$main_script"
    
    # Создаём симлинк в /usr/local/bin
    local target="/usr/local/bin/system-config"
    
    if [[ -L "$target" ]]; then
        warn "Команда system-config уже существует"
        read -p "Перезаписать? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "Установка отменена"
            return 0
        fi
        rm -f "$target"
    fi
    
    ln -s "$main_script" "$target"
    
    info "✅ Команда system-config установлена"
    info "Теперь вы можете запустить: system-config"
    
    return 0
}

################################################################################
# ДЕИНСТАЛЛЯЦИЯ
################################################################################

uninstall_system_config() {
    step "Удаление команды system-config..."
    
    local target="/usr/local/bin/system-config"
    
    if [[ -L "$target" ]]; then
        rm -f "$target"
        info "✅ Команда system-config удалена"
    else
        warn "Команда system-config не установлена"
    fi
    
    return 0
}

################################################################################
# ПРОВЕРКА
################################################################################

check_installation() {
    step "Проверка установки..."
    
    local target="/usr/local/bin/system-config"
    
    if [[ -L "$target" ]]; then
        local real_path=$(readlink -f "$target")
        info "✅ Команда установлена"
        info "   Симлинк: $target"
        info "   Указывает на: $real_path"
        
        if [[ -x "$real_path" ]]; then
            info "   Скрипт исполняемый: ДА"
        else
            warn "   Скрипт исполняемый: НЕТ"
        fi
    else
        warn "Команда system-config не установлена"
        info "Запустите: sudo ./install-global-command.sh install"
    fi
    
    return 0
}

################################################################################
# ОБНОВЛЕНИЕ
################################################################################

update_system_config() {
    step "Обновление system-config..."
    
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Если это git репозиторий
    if [[ -d "$script_dir/.git" ]]; then
        info "Обнаружен Git репозиторий"
        cd "$script_dir"
        
        git fetch origin
        local local_commit=$(git rev-parse HEAD)
        local remote_commit=$(git rev-parse origin/main 2>/dev/null || git rev-parse origin/master)
        
        if [[ "$local_commit" == "$remote_commit" ]]; then
            info "Уже используется последняя версия"
        else
            info "Доступно обновление"
            git pull
            info "✅ Обновление завершено"
            
            # Переустанавливаем команду
            install_system_config
        fi
    else
        warn "Не Git репозиторий. Автообновление недоступно"
    fi
    
    return 0
}

################################################################################
# МЕНЮ
################################################################################

show_menu() {
    cat <<MENU

╔═══════════════════════════════════════════════════════════╗
║         System Config - Установщик команды                ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  1) Установить команду system-config                     ║
║  2) Удалить команду system-config                        ║
║  3) Проверить установку                                  ║
║  4) Обновить до последней версии                         ║
║  0) Выход                                                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

MENU
    
    read -p "Выберите действие: " choice
    
    case $choice in
        1) install_system_config ;;
        2) uninstall_system_config ;;
        3) check_installation ;;
        4) update_system_config ;;
        0) exit 0 ;;
        *) error "Неверный выбор" ;;
    esac
}

################################################################################
# ТОЧКА ВХОДА
################################################################################

main() {
    if [[ $EUID -ne 0 ]]; then
        error "Требуются права root"
        echo "Запустите: sudo $0 $@"
        exit 1
    fi
    
    case "${1:-menu}" in
        install) install_system_config ;;
        uninstall) uninstall_system_config ;;
        check) check_installation ;;
        update) update_system_config ;;
        menu) show_menu ;;
        *)
            echo "Использование: $0 {install|uninstall|check|update|menu}"
            exit 1
            ;;
    esac
}

main "$@"
