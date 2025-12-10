#!/bin/bash
################################################################################
# Enterprise Module Loader - Модульная система загрузки с DI
# Version: 9.0.0
# Автор: Sandrick Tech
################################################################################

set -euo pipefail

# Глобальные переменные
declare -g ENTERPRISE_BASE="/opt/enterprise-deploy"
declare -g CONFIG_FILE="$ENTERPRISE_BASE/config/enterprise-config.yaml"
declare -gA LOADED_MODULES=()
declare -gA MODULE_DEPENDENCIES=()
declare -gA MODULE_STATUS=()
declare -g LOAD_ORDER=()

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

################################################################################
# ЛОГИРОВАНИЕ
################################################################################

log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S.%3N')
    
    case $level in
        DEBUG) echo -e "${CYAN}[DEBUG]${NC} [$timestamp] $message" ;;
        INFO)  echo -e "${GREEN}[INFO]${NC}  [$timestamp] $message" ;;
        WARN)  echo -e "${YELLOW}[WARN]${NC}  [$timestamp] $message" ;;
        ERROR) echo -e "${RED}[ERROR]${NC} [$timestamp] $message" ;;
    esac
    
    # JSON логирование
    if command -v jq &>/dev/null; then
        jq -n \
            --arg ts "$timestamp" \
            --arg lvl "$level" \
            --arg msg "$message" \
            --arg pid "$$" \
            '{timestamp: $ts, level: $lvl, message: $msg, pid: $pid}' \
            >> "$ENTERPRISE_BASE/logs/loader.json" 2>/dev/null || true
    fi
}

################################################################################
# ПАРСИНГ YAML КОНФИГУРАЦИИ
################################################################################

parse_yaml() {
    local yaml_file=$1
    local prefix=${2:-""}
    
    if ! command -v python3 &>/dev/null; then
        log ERROR "Python3 не установлен, необходим для парсинга YAML"
        return 1
    fi
    
    python3 - "$yaml_file" "$prefix" <<'PYTHON_SCRIPT'
import sys
import yaml

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}_{i}", sep=sep).items())
                else:
                    items.append((f"{new_key}_{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)

try:
    with open(sys.argv[1], 'r') as f:
        config = yaml.safe_load(f)
    
    flat = flatten_dict(config)
    prefix = sys.argv[2]
    
    for key, value in flat.items():
        var_name = f"{prefix}{key}".upper().replace('-', '_')
        if isinstance(value, bool):
            value = 'true' if value else 'false'
        print(f"declare -g {var_name}='{value}'")
except Exception as e:
    print(f"# ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT
}

################################################################################
# ЗАГРУЗКА КОНФИГУРАЦИИ
################################################################################

load_config() {
    log INFO "Загрузка конфигурации: $CONFIG_FILE"
    
    if [[ ! -f "$CONFIG_FILE" ]]; then
        log ERROR "Конфигурационный файл не найден: $CONFIG_FILE"
        return 1
    fi
    
    # Парсим YAML в переменные окружения
    local config_vars=$(parse_yaml "$CONFIG_FILE" "CFG_")
    if [[ $? -eq 0 ]]; then
        eval "$config_vars"
        log INFO "✅ Конфигурация загружена: ${CFG_SYSTEM_NAME} v${CFG_SYSTEM_VERSION}"
    else
        log ERROR "❌ Ошибка парсинга конфигурации"
        return 1
    fi
}

################################################################################
# ПРОВЕРКА ЗАВИСИМОСТЕЙ МОДУЛЯ
################################################################################

check_dependencies() {
    local module=$1
    local deps_var="MODULE_DEPS_${module^^}"
    
    if [[ -z "${!deps_var:-}" ]]; then
        return 0  # Нет зависимостей
    fi
    
    local deps=(${!deps_var})
    for dep in "${deps[@]}"; do
        if [[ -z "${LOADED_MODULES[$dep]:-}" ]]; then
            log ERROR "Модуль $module требует зависимость: $dep (не загружен)"
            return 1
        fi
    done
    
    return 0
}

################################################################################
# ЗАГРУЗКА МОДУЛЯ
################################################################################

load_module() {
    local module=$1
    local module_path="$ENTERPRISE_BASE/lib/${module}.sh"
    
    # Проверка кеша
    if [[ -n "${LOADED_MODULES[$module]:-}" ]]; then
        log DEBUG "Модуль $module уже загружен"
        return 0
    fi
    
    log INFO "⏳ Загрузка модуля: $module"
    
    # Проверка существования файла
    if [[ ! -f "$module_path" ]]; then
        log ERROR "Модуль не найден: $module_path"
        MODULE_STATUS[$module]="ERROR"
        return 1
    fi
    
    # Проверка зависимостей
    if ! check_dependencies "$module"; then
        MODULE_STATUS[$module]="DEPS_FAILED"
        return 1
    fi
    
    # Загрузка модуля
    if source "$module_path"; then
        LOADED_MODULES[$module]=1
        MODULE_STATUS[$module]="LOADED"
        LOAD_ORDER+=("$module")
        log INFO "✅ Модуль загружен: $module"
        
        # Вызов инициализации модуля, если существует
        if declare -f "${module}_init" &>/dev/null; then
            log DEBUG "Вызов ${module}_init()"
            "${module}_init"
        fi
        
        return 0
    else
        MODULE_STATUS[$module]="LOAD_FAILED"
        log ERROR "❌ Ошибка загрузки модуля: $module"
        return 1
    fi
}

################################################################################
# ЗАГРУЗКА МОДУЛЕЙ ПО ПРИОРИТЕТУ
################################################################################

load_modules_by_priority() {
    log INFO "Загрузка модулей по приоритету..."
    
    # Получаем список модулей из конфигурации
    local modules=$(python3 - "$CONFIG_FILE" <<'PYTHON'
import sys
import yaml

with open(sys.argv[1], 'r') as f:
    config = yaml.safe_load(f)

modules_list = []
for category, modules in config.get('modules', {}).items():
    if isinstance(modules, list):
        for module in modules:
            if isinstance(module, dict) and module.get('enabled', False):
                modules_list.append({
                    'name': module['name'],
                    'priority': module.get('priority', 999),
                    'dependencies': module.get('dependencies', [])
                })

# Сортировка по приоритету
modules_list.sort(key=lambda x: x['priority'])

for m in modules_list:
    print(f"{m['name']}|{m['priority']}|{','.join(m['dependencies'])}")
PYTHON
)
    
    local failed_modules=()
    local loaded_count=0
    
    while IFS='|' read -r module priority deps; do
        # Сохраняем зависимости
        MODULE_DEPENDENCIES[$module]="$deps"
        MODULE_DEPS_${module^^}="$deps"
        
        # Загружаем модуль
        if load_module "$module"; then
            ((loaded_count++))
        else
            failed_modules+=("$module")
        fi
        
        # Небольшая задержка для визуализации
        sleep 0.1
    done <<< "$modules"
    
    log INFO "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log INFO "✅ Загружено модулей: $loaded_count"
    
    if [[ ${#failed_modules[@]} -gt 0 ]]; then
        log WARN "❌ Не удалось загрузить: ${failed_modules[*]}"
    fi
}

################################################################################
# ЗАГРУЗКА ПРОФИЛЯ РАЗВЕРТЫВАНИЯ
################################################################################

load_deployment_profile() {
    local profile=${1:-"standard"}
    
    log INFO "Загрузка профиля развертывания: $profile"
    
    local profile_modules=$(python3 - "$CONFIG_FILE" "$profile" <<'PYTHON'
import sys
import yaml

with open(sys.argv[1], 'r') as f:
    config = yaml.safe_load(f)

profile = sys.argv[2]
profiles = config.get('deployment_profiles', {})

if profile not in profiles:
    print(f"ERROR: Profile {profile} not found", file=sys.stderr)
    sys.exit(1)

modules = profiles[profile]['modules']
if '*' in modules:
    # Загружаем все модули
    for category, mods in config.get('modules', {}).items():
        if isinstance(mods, list):
            for m in mods:
                if isinstance(m, dict) and m.get('enabled'):
                    print(m['name'])
else:
    for m in modules:
        print(m)
PYTHON
)
    
    if [[ $? -ne 0 ]]; then
        log ERROR "Профиль $profile не найден"
        return 1
    fi
    
    log INFO "Модули профиля: $(echo "$profile_modules" | tr '\n' ' ')"
    
    # Загружаем модули профиля
    while read -r module; do
        [[ -z "$module" ]] && continue
        load_module "$module"
    done <<< "$profile_modules"
}

################################################################################
# ПРОВЕРКА ЗДОРОВЬЯ СИСТЕМЫ
################################################################################

health_check() {
    log INFO "Проверка здоровья системы..."
    
    local healthy=true
    local checks=(
        "CPU:$(top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1)"
        "RAM:$(free | grep Mem | awk '{printf \"%.0f\", $3/$2 * 100.0}')"
        "DISK:$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')"
    )
    
    for check in "${checks[@]}"; do
        local metric="${check%%:*}"
        local value="${check##*:}"
        
        case $metric in
            CPU)
                if (( $(echo "$value > ${CFG_MONITORING_ALERTS_CPU_THRESHOLD:-85}" | bc -l) )); then
                    log WARN "⚠️  CPU перегружен: ${value}%"
                    healthy=false
                else
                    log INFO "✅ CPU: ${value}%"
                fi
                ;;
            RAM)
                if (( value > ${CFG_MONITORING_ALERTS_MEMORY_THRESHOLD:-90} )); then
                    log WARN "⚠️  RAM перегружен: ${value}%"
                    healthy=false
                else
                    log INFO "✅ RAM: ${value}%"
                fi
                ;;
            DISK)
                if (( value > ${CFG_MONITORING_ALERTS_DISK_THRESHOLD:-80} )); then
                    log WARN "⚠️  Диск заполнен: ${value}%"
                    healthy=false
                else
                    log INFO "✅ Диск: ${value}%"
                fi
                ;;
        esac
    done
    
    if $healthy; then
        log INFO "🟢 Система здорова"
        return 0
    else
        log WARN "🟡 Обнаружены проблемы"
        return 1
    fi
}

################################################################################
# ВЫВОД СТАТУСА МОДУЛЕЙ
################################################################################

show_module_status() {
    log INFO "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log INFO "Статус модулей:"
    
    for module in "${LOAD_ORDER[@]}"; do
        local status="${MODULE_STATUS[$module]:-UNKNOWN}"
        local deps="${MODULE_DEPENDENCIES[$module]:-none}"
        
        case $status in
            LOADED)
                log INFO "  ✅ $module (deps: $deps)"
                ;;
            ERROR|LOAD_FAILED|DEPS_FAILED)
                log ERROR "  ❌ $module - $status"
                ;;
            *)
                log WARN "  ⚠️  $module - $status"
                ;;
        esac
    done
    
    log INFO "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

################################################################################
# ВЫГРУЗКА МОДУЛЕЙ
################################################################################

unload_modules() {
    log INFO "Выгрузка модулей..."
    
    # Выгружаем в обратном порядке
    for ((i=${#LOAD_ORDER[@]}-1; i>=0; i--)); do
        local module="${LOAD_ORDER[$i]}"
        
        # Вызов деинициализации, если существует
        if declare -f "${module}_cleanup" &>/dev/null; then
            log DEBUG "Вызов ${module}_cleanup()"
            "${module}_cleanup"
        fi
        
        unset LOADED_MODULES[$module]
        log INFO "  ✅ Выгружен: $module"
    done
    
    LOAD_ORDER=()
    log INFO "Все модули выгружены"
}

################################################################################
# ИНТЕРАКТИВНЫЙ РЕЖИМ
################################################################################

interactive_mode() {
    log INFO "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log INFO "Enterprise Module Loader - Interactive Mode"
    log INFO "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    while true; do
        echo ""
        echo "Команды:"
        echo "  load <module>    - Загрузить модуль"
        echo "  unload <module>  - Выгрузить модуль"
        echo "  status           - Показать статус"
        echo "  health           - Проверка здоровья"
        echo "  reload           - Перезагрузить все"
        echo "  quit             - Выход"
        echo ""
        read -p "> " cmd args
        
        case $cmd in
            load)
                load_module "$args"
                ;;
            unload)
                log INFO "Выгрузка модуля: $args"
                unset LOADED_MODULES[$args]
                ;;
            status)
                show_module_status
                ;;
            health)
                health_check
                ;;
            reload)
                unload_modules
                load_modules_by_priority
                ;;
            quit|exit)
                log INFO "Выход..."
                break
                ;;
            *)
                log ERROR "Неизвестная команда: $cmd"
                ;;
        esac
    done
}

################################################################################
# ГЛАВНАЯ ФУНКЦИЯ
################################################################################

main() {
    log INFO "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log INFO "Enterprise Module Loader v9.0.0"
    log INFO "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Создание необходимых директорий
    mkdir -p "$ENTERPRISE_BASE"/{lib,logs,config,data}
    
    # Загрузка конфигурации
    if ! load_config; then
        log ERROR "Критическая ошибка загрузки конфигурации"
        exit 1
    fi
    
    # Проверка аргументов
    case "${1:-auto}" in
        auto)
            load_modules_by_priority
            health_check
            show_module_status
            ;;
        profile)
            load_deployment_profile "${2:-standard}"
            health_check
            show_module_status
            ;;
        interactive)
            interactive_mode
            ;;
        module)
            load_module "$2"
            ;;
        health)
            health_check
            ;;
        *)
            log ERROR "Неизвестный режим: $1"
            echo "Использование: $0 [auto|profile|interactive|module|health]"
            exit 1
            ;;
    esac
    
    log INFO "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log INFO "Загрузка завершена"
}

# Запуск
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
