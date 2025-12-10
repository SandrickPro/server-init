#!/bin/bash
################################################################################
# SRV-SYS IPTABLES CONTROLLER v1.0
# Автор: Sandrick Tech
# Дата: 2024-12-08
# Описание: Централизованный контроллер iptables согласно ТЗ histor.txt
#
# Основной функционал:
#   - Интерактивное управление портами и сервисами
#   - Модульная структура правил iptables (активные/неактивные)
#   - Генерация combined.v4/v6 для автоматического восстановления
#   - Создание systemd юнита iptables-restore.service
#   - Полная совместимость с /srv/sys/ архитектурой
#
# Структура:
#   /srv/sys/iptables/v4/*.v4         - активные правила IPv4
#   /srv/sys/iptables/v4/*.v4.inactive - неактивные правила IPv4
#   /srv/sys/iptables/v6/*.v6         - активные правила IPv6
#   /srv/sys/iptables/v6/*.v6.inactive - неактивные правила IPv6
#   /srv/sys/iptables/v4/combined.v4  - объединённые правила IPv4
#   /srv/sys/iptables/v6/combined.v6  - объединённые правила IPv6
################################################################################

# Строгий режим выполнения
set -euo pipefail

################################################################################
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
################################################################################

# Базовый путь для всей системы /srv/sys
BASE_DIR="/srv/sys"

# Директории для iptables правил
IPT_V4_DIR="$BASE_DIR/iptables/v4"
IPT_V6_DIR="$BASE_DIR/iptables/v6"

# Директория для systemd юнитов
SYSTEMD_DIR="$BASE_DIR/systemd/system"

# Лог-файл операций
LOG_FILE="/var/log/srv-sys-iptables.log"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Массив поддерживаемых сервисов (расширяемый)
# Формат: "service_name:port:protocol:description"
declare -A SERVICES=(
    ["ssh"]="22:tcp:SSH доступ"
    ["smtp"]="25:tcp:Почтовый сервер (SMTP)"
    ["dns"]="53:udp:DNS сервер"
    ["http"]="80:tcp:Веб-сервер HTTP"
    ["pop3"]="110:tcp:Почтовый сервер (POP3)"
    ["imap"]="143:tcp:Почтовый сервер (IMAP)"
    ["https"]="443:tcp:Веб-сервер HTTPS"
    ["smtps"]="465:tcp:Почтовый сервер (SMTPS)"
    ["imaps"]="993:tcp:Почтовый сервер (IMAPS)"
    ["pop3s"]="995:tcp:Почтовый сервер (POP3S)"
    ["mysql"]="3306:tcp:MySQL база данных"
    ["postgresql"]="5432:tcp:PostgreSQL база данных"
    ["mongodb"]="27017:tcp:MongoDB база данных"
    ["redis"]="6379:tcp:Redis кеш"
    ["ftp"]="21:tcp:FTP сервер"
    ["ftps"]="990:tcp:FTPS сервер"
    ["ssh-alt"]="2222:tcp:SSH альтернативный порт"
    ["openvpn"]="1194:udp:OpenVPN"
    ["wireguard"]="51820:udp:WireGuard VPN"
)

################################################################################
# УТИЛИТЫ И ЛОГИРОВАНИЕ
################################################################################

###
# Функция: log_message
# Описание: Логирование сообщений с timestamp
# Параметры:
#   $1 - уровень (INFO/WARN/ERROR)
#   $2 - сообщение
###
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Записываем в лог-файл
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

###
# Функция: info
# Описание: Вывод информационного сообщения
###
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
    log_message "INFO" "$1"
}

###
# Функция: warn
# Описание: Вывод предупреждения
###
warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    log_message "WARN" "$1"
}

###
# Функция: error
# Описание: Вывод ошибки
###
error() {
    echo -e "${RED}[ERROR]${NC} $1"
    log_message "ERROR" "$1"
}

###
# Функция: banner
# Описание: Вывод ASCII-арт баннера
###
banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║           IPTABLES CONTROLLER v1.0 - /srv/sys/                   ║
║                                                                   ║
║     Централизованное управление портами и правилами firewall     ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

################################################################################
# ИНИЦИАЛИЗАЦИЯ СТРУКТУРЫ ДИРЕКТОРИЙ
################################################################################

###
# Функция: create_directory_structure
# Описание: Создание всей структуры директорий /srv/sys для iptables
# Вызывается: При первом запуске скрипта
###
create_directory_structure() {
    info "Создание структуры директорий /srv/sys..."
    
    # Создаём базовую директорию
    mkdir -p "$BASE_DIR"
    
    # Создаём директории для iptables правил (IPv4 и IPv6)
    mkdir -p "$IPT_V4_DIR"
    mkdir -p "$IPT_V6_DIR"
    
    # Создаём директорию для systemd юнитов
    mkdir -p "$SYSTEMD_DIR"
    
    # Создаём директории для SSH (если не существуют)
    mkdir -p "$BASE_DIR/ssh/win_config"
    mkdir -p "$BASE_DIR/ssh/sshd_config.d"
    mkdir -p "$BASE_DIR/ssh/ssh_session"
    
    # Создаём директории для аудита
    mkdir -p "$BASE_DIR/audit/rules.d"
    
    # Создаём директории для sudoers
    mkdir -p "$BASE_DIR/sudoers.d"
    
    # Создаём директории для резервных копий
    mkdir -p "$BASE_DIR/backups"
    
    # Устанавливаем корректные права
    chmod 755 "$BASE_DIR"
    chmod 755 "$IPT_V4_DIR"
    chmod 755 "$IPT_V6_DIR"
    chmod 755 "$SYSTEMD_DIR"
    
    info "Структура директорий создана успешно"
}

################################################################################
# ГЕНЕРАЦИЯ ПРАВИЛ IPTABLES
################################################################################

###
# Функция: generate_base_rules_v4
# Описание: Генерация базовых правил iptables для IPv4
# Параметры: Нет
# Возвращает: Строку с базовыми правилами
###
generate_base_rules_v4() {
    cat <<'EOF'
*filter
# Базовые политики: DROP для всего входящего, ACCEPT для исходящего
:INPUT DROP [0:0]
:FORWARD DROP [0:0]
:OUTPUT ACCEPT [0:0]

# Разрешаем loopback (локальные соединения)
-A INPUT -i lo -j ACCEPT

# Разрешаем установленные и связанные соединения
-A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Защита от некоторых атак
# Блокируем invalid пакеты
-A INPUT -m conntrack --ctstate INVALID -j DROP

# Защита от SYN flood
-A INPUT -p tcp --syn -m limit --limit 1/s --limit-burst 3 -j ACCEPT

# Разрешаем ICMP (ping) с ограничением
-A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/s -j ACCEPT
-A INPUT -p icmp -j DROP

EOF
}

###
# Функция: generate_base_rules_v6
# Описание: Генерация базовых правил iptables для IPv6
# Параметры: Нет
# Возвращает: Строку с базовыми правилами
###
generate_base_rules_v6() {
    cat <<'EOF'
*filter
# Базовые политики для IPv6
:INPUT DROP [0:0]
:FORWARD DROP [0:0]
:OUTPUT ACCEPT [0:0]

# Разрешаем loopback
-A INPUT -i lo -j ACCEPT

# Разрешаем установленные соединения
-A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Блокируем invalid пакеты
-A INPUT -m conntrack --ctstate INVALID -j DROP

# Разрешаем ICMPv6 (необходим для работы IPv6)
-A INPUT -p ipv6-icmp -j ACCEPT

EOF
}

###
# Функция: generate_service_rule
# Описание: Генерация правила iptables для конкретного сервиса
# Параметры:
#   $1 - имя сервиса (ssh, http, mysql и т.д.)
#   $2 - порт
#   $3 - протокол (tcp/udp)
#   $4 - версия IP (4 или 6)
# Возвращает: Строку с правилом iptables
###
generate_service_rule() {
    local service="$1"
    local port="$2"
    local protocol="$3"
    local ip_version="$4"
    
    cat <<EOF
# Правило для сервиса: $service (порт $port/$protocol)
-A INPUT -p $protocol --dport $port -m conntrack --ctstate NEW -j ACCEPT

EOF
}

###
# Функция: create_service_file
# Описание: Создание файла правил для сервиса
# Параметры:
#   $1 - имя сервиса
#   $2 - активен ли сервис (true/false)
###
create_service_file() {
    local service="$1"
    local is_active="$2"
    
    # Получаем информацию о сервисе из массива
    local service_info="${SERVICES[$service]}"
    IFS=':' read -r port protocol description <<< "$service_info"
    
    # Определяем расширение файла (активный или неактивный)
    local v4_suffix=".v4"
    local v6_suffix=".v6"
    
    if [[ "$is_active" == "false" ]]; then
        v4_suffix=".v4.inactive"
        v6_suffix=".v6.inactive"
    fi
    
    # Пути к файлам
    local v4_file="$IPT_V4_DIR/${service}${v4_suffix}"
    local v6_file="$IPT_V6_DIR/${service}${v6_suffix}"
    
    # Создаём файл для IPv4
    {
        echo "# Сервис: $service"
        echo "# Описание: $description"
        echo "# Порт: $port/$protocol"
        echo "# Статус: $([ "$is_active" == "true" ] && echo "АКТИВЕН" || echo "НЕАКТИВЕН")"
        echo "# Дата создания: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        generate_service_rule "$service" "$port" "$protocol" "4"
    } > "$v4_file"
    
    # Создаём файл для IPv6
    {
        echo "# Сервис: $service"
        echo "# Описание: $description"
        echo "# Порт: $port/$protocol"
        echo "# Статус: $([ "$is_active" == "true" ] && echo "АКТИВЕН" || echo "НЕАКТИВЕН")"
        echo "# Дата создания: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        generate_service_rule "$service" "$port" "$protocol" "6"
    } > "$v6_file"
    
    if [[ "$is_active" == "true" ]]; then
        info "Создан активный сервис: $service (порт $port/$protocol)"
    else
        info "Создан неактивный сервис: $service (порт $port/$protocol)"
    fi
}

################################################################################
# ОБЪЕДИНЕНИЕ ПРАВИЛ
################################################################################

###
# Функция: combine_rules
# Описание: Объединение всех активных правил в combined.v4 и combined.v6
# Параметры: Нет
###
combine_rules() {
    info "Объединение правил iptables..."
    
    local combined_v4="$IPT_V4_DIR/combined.v4"
    local combined_v6="$IPT_V6_DIR/combined.v6"
    
    # Создаём combined.v4
    {
        echo "# Combined iptables rules (IPv4)"
        echo "# Автоматически сгенерировано: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "# НЕ РЕДАКТИРУЙТЕ ВРУЧНУЮ! Используйте srv-sys-iptables-controller.sh"
        echo ""
        
        # Добавляем базовые правила
        generate_base_rules_v4
        
        # Добавляем все активные правила сервисов (только файлы без .inactive)
        for rule_file in "$IPT_V4_DIR"/*.v4; do
            # Пропускаем combined.v4 и несуществующие файлы
            [[ "$rule_file" == "$combined_v4" ]] && continue
            [[ ! -f "$rule_file" ]] && continue
            
            # Добавляем правило
            echo "# Включено из: $(basename "$rule_file")"
            grep -v '^#' "$rule_file" | grep -v '^$'  # Фильтруем комментарии и пустые строки
            echo ""
        done
        
        # Закрываем таблицу filter
        echo "COMMIT"
    } > "$combined_v4"
    
    # Создаём combined.v6
    {
        echo "# Combined iptables rules (IPv6)"
        echo "# Автоматически сгенерировано: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "# НЕ РЕДАКТИРУЙТЕ ВРУЧНУЮ! Используйте srv-sys-iptables-controller.sh"
        echo ""
        
        # Добавляем базовые правила
        generate_base_rules_v6
        
        # Добавляем все активные правила сервисов
        for rule_file in "$IPT_V6_DIR"/*.v6; do
            # Пропускаем combined.v6 и несуществующие файлы
            [[ "$rule_file" == "$combined_v6" ]] && continue
            [[ ! -f "$rule_file" ]] && continue
            
            # Добавляем правило
            echo "# Включено из: $(basename "$rule_file")"
            grep -v '^#' "$rule_file" | grep -v '^$'
            echo ""
        done
        
        # Закрываем таблицу filter
        echo "COMMIT"
    } > "$combined_v6"
    
    info "Объединённые правила созданы:"
    info "  - $combined_v4"
    info "  - $combined_v6"
}

################################################################################
# ПРИМЕНЕНИЕ ПРАВИЛ
################################################################################

###
# Функция: apply_rules
# Описание: Применение combined правил к текущей системе
# Параметры: Нет
###
apply_rules() {
    info "Применение правил iptables к системе..."
    
    local combined_v4="$IPT_V4_DIR/combined.v4"
    local combined_v6="$IPT_V6_DIR/combined.v6"
    
    # Проверяем существование файлов
    if [[ ! -f "$combined_v4" ]]; then
        error "Файл $combined_v4 не найден! Запустите combine_rules сначала."
        return 1
    fi
    
    # Применяем IPv4 правила
    info "Применение IPv4 правил..."
    if iptables-restore < "$combined_v4"; then
        info "IPv4 правила применены успешно"
    else
        error "Ошибка применения IPv4 правил!"
        return 1
    fi
    
    # Применяем IPv6 правила (если система поддерживает)
    if command -v ip6tables-restore &>/dev/null && [[ -f "$combined_v6" ]]; then
        info "Применение IPv6 правил..."
        if ip6tables-restore < "$combined_v6"; then
            info "IPv6 правила применены успешно"
        else
            warn "Ошибка применения IPv6 правил (возможно IPv6 не поддерживается)"
        fi
    fi
    
    info "Все правила применены к системе"
}

################################################################################
# SYSTEMD СЕРВИС ДЛЯ АВТОЗАГРУЗКИ
################################################################################

###
# Функция: create_iptables_restore_service
# Описание: Создание systemd юнита для восстановления правил при загрузке
# Параметры: Нет
###
create_iptables_restore_service() {
    info "Создание systemd юнита iptables-restore.service..."
    
    local service_file="$SYSTEMD_DIR/iptables-restore.service"
    
    cat > "$service_file" <<EOF
[Unit]
Description=Restore iptables firewall rules from /srv/sys/iptables
Documentation=man:iptables-restore(8)
# Запускаем до network-pre.target чтобы правила были готовы до поднятия сети
DefaultDependencies=no
Before=network-pre.target
Wants=network-pre.target

[Service]
Type=oneshot
# Восстанавливаем IPv4 правила
ExecStart=/usr/sbin/iptables-restore $IPT_V4_DIR/combined.v4
# Восстанавливаем IPv6 правила (если доступны)
ExecStart=-/usr/sbin/ip6tables-restore $IPT_V6_DIR/combined.v6
# RemainAfterExit=yes - считать сервис активным после запуска
RemainAfterExit=yes

[Install]
# Включать автоматически в multi-user.target (обычная загрузка)
WantedBy=multi-user.target
EOF
    
    info "Systemd юнит создан: $service_file"
    
    # Копируем в системную директорию systemd
    info "Копирование в /etc/systemd/system/..."
    cp "$service_file" /etc/systemd/system/
    
    # Перезагружаем конфигурацию systemd
    info "Перезагрузка конфигурации systemd..."
    systemctl daemon-reload
    
    # Включаем автозапуск
    info "Включение автозапуска iptables-restore.service..."
    systemctl enable iptables-restore.service
    
    info "Systemd юнит установлен и активирован"
}

################################################################################
# ИНТЕРАКТИВНОЕ УПРАВЛЕНИЕ
################################################################################

###
# Функция: ask_port_services
# Описание: Интерактивный выбор портов/сервисов для открытия
# Параметры: Нет
###
ask_port_services() {
    banner
    
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║         Настройка портов и сервисов для iptables                 ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Для каждого сервиса выберите: открыть порт (y) или оставить закрытым (n)${NC}"
    echo ""
    
    # Проходим по всем сервисам
    for service in "${!SERVICES[@]}"; do
        local service_info="${SERVICES[$service]}"
        IFS=':' read -r port protocol description <<< "$service_info"
        
        echo -e "${BLUE}────────────────────────────────────────────────────────────${NC}"
        echo -e "${CYAN}Сервис:${NC} $service"
        echo -e "${CYAN}Описание:${NC} $description"
        echo -e "${CYAN}Порт/Протокол:${NC} $port/$protocol"
        echo ""
        
        # Запрашиваем у пользователя
        read -rp "Открыть порт для сервиса $service? [y/N]: " answer
        
        case "$answer" in
            [yY]|[yY][eE][sS])
                create_service_file "$service" "true"
                ;;
            *)
                create_service_file "$service" "false"
                ;;
        esac
        
        echo ""
    done
    
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}Все сервисы настроены!${NC}"
    echo ""
}

###
# Функция: activate_service
# Описание: Активация ранее неактивного сервиса
# Параметры:
#   $1 - имя сервиса
###
activate_service() {
    local service="$1"
    
    # Проверяем существование сервиса
    if [[ ! -v "SERVICES[$service]" ]]; then
        error "Сервис '$service' не найден!"
        return 1
    fi
    
    local v4_inactive="$IPT_V4_DIR/${service}.v4.inactive"
    local v6_inactive="$IPT_V6_DIR/${service}.v6.inactive"
    local v4_active="$IPT_V4_DIR/${service}.v4"
    local v6_active="$IPT_V6_DIR/${service}.v6"
    
    # Проверяем существование неактивного файла
    if [[ ! -f "$v4_inactive" ]]; then
        warn "Сервис '$service' уже активен или не существует"
        return 1
    fi
    
    # Переименовываем файлы (активируем)
    mv "$v4_inactive" "$v4_active"
    mv "$v6_inactive" "$v6_active"
    
    info "Сервис '$service' активирован"
    
    # Пересобираем combined правила
    combine_rules
}

###
# Функция: deactivate_service
# Описание: Деактивация активного сервиса
# Параметры:
#   $1 - имя сервиса
###
deactivate_service() {
    local service="$1"
    
    # Проверяем существование сервиса
    if [[ ! -v "SERVICES[$service]" ]]; then
        error "Сервис '$service' не найден!"
        return 1
    fi
    
    local v4_active="$IPT_V4_DIR/${service}.v4"
    local v6_active="$IPT_V6_DIR/${service}.v6"
    local v4_inactive="$IPT_V4_DIR/${service}.v4.inactive"
    local v6_inactive="$IPT_V6_DIR/${service}.v6.inactive"
    
    # Проверяем существование активного файла
    if [[ ! -f "$v4_active" ]]; then
        warn "Сервис '$service' уже неактивен или не существует"
        return 1
    fi
    
    # Переименовываем файлы (деактивируем)
    mv "$v4_active" "$v4_inactive"
    mv "$v6_active" "$v6_inactive"
    
    info "Сервис '$service' деактивирован"
    
    # Пересобираем combined правила
    combine_rules
}

###
# Функция: show_active_rules
# Описание: Показать все активные правила
# Параметры: Нет
###
show_active_rules() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}          АКТИВНЫЕ ПРАВИЛА IPTABLES                         ${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    echo -e "${GREEN}IPv4 правила (активные):${NC}"
    for rule_file in "$IPT_V4_DIR"/*.v4; do
        [[ "$rule_file" == "$IPT_V4_DIR/combined.v4" ]] && continue
        [[ ! -f "$rule_file" ]] && continue
        
        local service=$(basename "$rule_file" .v4)
        local service_info="${SERVICES[$service]:-Неизвестный сервис}"
        echo "  ✓ $service - $service_info"
    done
    
    echo ""
    echo -e "${YELLOW}IPv4 правила (неактивные):${NC}"
    for rule_file in "$IPT_V4_DIR"/*.v4.inactive; do
        [[ ! -f "$rule_file" ]] && continue
        
        local service=$(basename "$rule_file" .v4.inactive)
        local service_info="${SERVICES[$service]:-Неизвестный сервис}"
        echo "  ✗ $service - $service_info"
    done
    
    echo ""
}

################################################################################
# ГЛАВНОЕ МЕНЮ
################################################################################

###
# Функция: main_menu
# Описание: Главное интерактивное меню
# Параметры: Нет
###
main_menu() {
    while true; do
        banner
        
        echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${CYAN}║                     ГЛАВНОЕ МЕНЮ                                  ║${NC}"
        echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo "  1. Интерактивная настройка портов/сервисов"
        echo "  2. Активировать сервис"
        echo "  3. Деактивировать сервис"
        echo "  4. Показать активные правила"
        echo "  5. Пересобрать combined правила"
        echo "  6. Применить правила к системе"
        echo "  7. Создать/обновить systemd юнит"
        echo "  8. Показать текущие iptables правила"
        echo "  0. Выход"
        echo ""
        read -rp "Выберите действие: " choice
        
        case "$choice" in
            1)
                ask_port_services
                combine_rules
                read -rp "Применить правила к системе сейчас? [y/N]: " apply
                [[ "$apply" =~ ^[yY] ]] && apply_rules
                ;;
            2)
                read -rp "Введите имя сервиса для активации: " srv
                activate_service "$srv"
                read -rp "Применить правила к системе сейчас? [y/N]: " apply
                [[ "$apply" =~ ^[yY] ]] && apply_rules
                ;;
            3)
                read -rp "Введите имя сервиса для деактивации: " srv
                deactivate_service "$srv"
                read -rp "Применить правила к системе сейчас? [y/N]: " apply
                [[ "$apply" =~ ^[yY] ]] && apply_rules
                ;;
            4)
                show_active_rules
                read -rp "Нажмите Enter для продолжения..."
                ;;
            5)
                combine_rules
                info "Combined правила пересобраны"
                read -rp "Нажмите Enter для продолжения..."
                ;;
            6)
                apply_rules
                info "Правила применены к системе"
                read -rp "Нажмите Enter для продолжения..."
                ;;
            7)
                create_iptables_restore_service
                info "Systemd юнит создан/обновлён"
                read -rp "Нажмите Enter для продолжения..."
                ;;
            8)
                echo -e "${CYAN}Текущие правила iptables (IPv4):${NC}"
                iptables -L -n -v --line-numbers
                echo ""
                read -rp "Нажмите Enter для продолжения..."
                ;;
            0)
                info "Выход из программы"
                exit 0
                ;;
            *)
                warn "Неверный выбор, попробуйте снова"
                sleep 1
                ;;
        esac
    done
}

################################################################################
# ПРОВЕРКА ROOT И ЗАВИСИМОСТЕЙ
################################################################################

###
# Функция: check_root
# Описание: Проверка запуска от root
###
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "Этот скрипт должен быть запущен от root!"
        error "Используйте: sudo $0"
        exit 1
    fi
}

###
# Функция: check_dependencies
# Описание: Проверка наличия необходимых утилит
###
check_dependencies() {
    local deps=("iptables" "iptables-restore" "systemctl")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &>/dev/null; then
            missing+=("$dep")
        fi
    done
    
    if [[ ${#missing[@]} -gt 0 ]]; then
        error "Отсутствуют необходимые утилиты: ${missing[*]}"
        error "Установите их: apt-get install iptables systemd"
        exit 1
    fi
}

################################################################################
# ГЛАВНАЯ ФУНКЦИЯ
################################################################################

main() {
    # Проверки перед запуском
    check_root
    check_dependencies
    
    # Создаём структуру директорий
    create_directory_structure
    
    # Запускаем главное меню
    main_menu
}

# Запуск скрипта
main "$@"
