#!/bin/bash
################################################################################
# Local DNS Manager - Улучшенная версия v2
# Автор: Sandrick Tech
# Дата: 2024-12-09
# Описание: Управление локальным DNS (dnsmasq) с авто-сканированием сети
################################################################################

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

DNS_CONFIG="/etc/dnsmasq.d/local-dns.conf"
HOSTS_DB="/srv/sys/dns_hosts.db"
LOG_FILE="/srv/sys/logs/dns-manager.log"

info() { echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"; }
step() { echo -e "${BLUE}[STEP]${NC} $1" | tee -a "$LOG_FILE"; }
error() { echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"; }

################################################################################
# УСТАНОВКА
################################################################################

install_dnsmasq() {
    step "Установка dnsmasq..."
    
    # Останавливаем systemd-resolved (конфликт с портом 53)
    if systemctl is-active --quiet systemd-resolved; then
        warn "Отключение systemd-resolved (конфликт порта 53)..."
        systemctl stop systemd-resolved
        systemctl disable systemd-resolved
        rm -f /etc/resolv.conf
        echo "nameserver 8.8.8.8" > /etc/resolv.conf
        echo "nameserver 1.1.1.1" >> /etc/resolv.conf
    fi
    
    apt-get update -qq
    apt-get install -y dnsmasq dnsutils net-tools nmap
    
    # Базовая конфигурация
    cat > /etc/dnsmasq.conf <<EOF
# Базовая конфигурация dnsmasq
domain-needed
bogus-priv
no-resolv

# Upstream DNS
server=8.8.8.8
server=1.1.1.1
server=1.0.0.1

# Локальный домен
local=/local/
domain=local
expand-hosts

# Интерфейсы
listen-address=127.0.0.1
listen-address=$(hostname -I | awk '{print $1}')
bind-interfaces

# Кеширование
cache-size=1000

# Логирование
log-queries
log-facility=$LOG_FILE

# Конфигурации
conf-dir=/etc/dnsmasq.d/,*.conf
EOF

    mkdir -p /etc/dnsmasq.d
    mkdir -p "$(dirname $HOSTS_DB)"
    mkdir -p "$(dirname $LOG_FILE)"
    
    touch "$DNS_CONFIG"
    touch "$HOSTS_DB"
    
    systemctl restart dnsmasq
    systemctl enable dnsmasq
    
    info "✅ DNS сервер установлен и запущен"
    dialog --msgbox "✅ DNS сервер установлен\n\nПорт: 53\nДомен: .local\nUpstream: 8.8.8.8, 1.1.1.1" 10 45
}

################################################################################
# СКАНИРОВАНИЕ СЕТИ
################################################################################

scan_network() {
    step "Сканирование локальной сети..."
    
    local my_ip=$(hostname -I | awk '{print $1}')
    local network=$(echo "$my_ip" | awk -F. '{print $1"."$2"."$3".0/24"}')
    
    dialog --infobox "Сканирование $network...\n\nЭто может занять 1-2 минуты" 7 45
    
    local results=$(mktemp)
    local details=$(mktemp)
    
    # Быстрый ping sweep
    for i in {1..254}; do
        local ip=$(echo "$network" | sed "s/0\/24/$i/")
        (ping -c 1 -W 1 "$ip" &>/dev/null && echo "$ip" >> "$results") &
    done
    
    wait
    
    if [[ ! -s "$results" ]]; then
        dialog --msgbox "❌ Хосты не найдены в сети $network" 7 50
        rm -f "$results" "$details"
        return
    fi
    
    local found=$(wc -l < "$results")
    
    echo "╔══════════════════════════════════════════════════════╗" > "$details"
    echo "║     СКАНИРОВАНИЕ СЕТИ: $network     ║" >> "$details"
    echo "╚══════════════════════════════════════════════════════╝" >> "$details"
    echo "" >> "$details"
    echo "Найдено устройств: $found" >> "$details"
    echo "" >> "$details"
    printf "%-17s %-25s %s\n" "IP ADDRESS" "HOSTNAME" "STATUS" >> "$details"
    echo "──────────────────────────────────────────────────────────" >> "$details"
    
    while IFS= read -r ip; do
        local hostname=$(nslookup "$ip" 2>/dev/null | grep "name =" | awk '{print $NF}' | sed 's/\.$//')
        [[ -z "$hostname" ]] && hostname=$(dig -x "$ip" +short 2>/dev/null | sed 's/\.$//')
        [[ -z "$hostname" ]] && hostname="unknown"
        
        printf "%-17s %-25s %s\n" "$ip" "$hostname" "Online" >> "$details"
    done < "$results"
    
    echo "" >> "$details"
    echo "Совет: используйте 'Массовое добавление' для импорта" >> "$details"
    
    dialog --title "Результаты сканирования" --textbox "$details" 20 70
    
    rm -f "$results" "$details"
}

################################################################################
# УПРАВЛЕНИЕ ЗАПИСЯМИ
################################################################################

add_dns_record() {
    local hostname=""
    local ip=""
    local description=""
    
    exec 3>&1
    hostname=$(dialog --inputbox "Имя хоста (без .local):\n\nПример: server1" 10 50 3>&1 1>&2 2>&3)
    exitcode=$?
    exec 3>&-
    
    [[ $exitcode -ne 0 || -z "$hostname" ]] && return
    
    exec 3>&1
    ip=$(dialog --inputbox "IP адрес:\n\nПример: 192.168.1.100" 10 50 3>&1 1>&2 2>&3)
    exitcode=$?
    exec 3>&-
    
    [[ $exitcode -ne 0 || -z "$ip" ]] && return
    
    # Валидация IP
    if ! [[ "$ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        dialog --msgbox "❌ Неверный формат IP адреса\n\nПример: 192.168.1.100" 8 40
        return
    fi
    
    exec 3>&1
    description=$(dialog --inputbox "Описание (опционально):" 8 50 3>&1 1>&2 2>&3)
    exec 3>&-
    
    # Добавляем в конфиг
    echo "address=/$hostname.local/$ip" >> "$DNS_CONFIG"
    
    # Сохраняем в базу
    echo "$hostname.local|$ip|$description|$(date '+%Y-%m-%d %H:%M:%S')" >> "$HOSTS_DB"
    
    systemctl restart dnsmasq
    
    dialog --msgbox "✅ Запись добавлена:\n\n$hostname.local -> $ip\n\nПроверка:\nping $hostname.local\nnslookup $hostname.local" 12 50
}

bulk_add_records() {
    local temp_file=$(mktemp)
    
    dialog --title "Массовое добавление DNS записей" \
        --inputbox "Введите записи (формат: hostname IP):\n\nПример:\nserver1 192.168.1.10\nserver2 192.168.1.11\nnas 192.168.1.50\n\nОдна запись на строку" \
        18 60 2> "$temp_file"
    
    if [[ ! -s "$temp_file" ]]; then
        rm -f "$temp_file"
        return
    fi
    
    local count=0
    local added=$(mktemp)
    
    while IFS= read -r line; do
        [[ -z "$line" || "$line" =~ ^# ]] && continue
        
        local hostname=$(echo "$line" | awk '{print $1}')
        local ip=$(echo "$line" | awk '{print $2}')
        
        if [[ -n "$hostname" && -n "$ip" && "$ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            echo "address=/$hostname.local/$ip" >> "$DNS_CONFIG"
            echo "$hostname.local|$ip|Bulk import|$(date '+%Y-%m-%d %H:%M:%S')" >> "$HOSTS_DB"
            echo "$hostname.local -> $ip" >> "$added"
            ((count++))
        fi
    done < "$temp_file"
    
    if [[ $count -gt 0 ]]; then
        systemctl restart dnsmasq
        echo "" >> "$added"
        echo "Всего добавлено: $count записей" >> "$added"
        dialog --title "Импорт завершён" --textbox "$added" 15 50
    else
        dialog --msgbox "❌ Не добавлено ни одной записи\n\nПроверьте формат" 8 40
    fi
    
    rm -f "$temp_file" "$added"
}

remove_dns_record() {
    if [[ ! -f "$DNS_CONFIG" || ! -s "$DNS_CONFIG" ]]; then
        dialog --msgbox "Нет записей для удаления" 6 30
        return
    fi
    
    local records=()
    while IFS= read -r line; do
        if [[ "$line" =~ address=/(.*)/(.*) ]]; then
            records+=("${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}")
        fi
    done < "$DNS_CONFIG"
    
    if [[ ${#records[@]} -eq 0 ]]; then
        dialog --msgbox "Нет записей" 6 25
        return
    fi
    
    local choice=$(dialog --menu "Выберите запись для удаления:" 15 60 8 "${records[@]}" 3>&1 1>&2 2>&3)
    
    if [[ -n "$choice" ]]; then
        sed -i "\|address=/$choice/|d" "$DNS_CONFIG"
        sed -i "\|^$choice||d" "$HOSTS_DB"
        systemctl restart dnsmasq
        dialog --msgbox "✅ Запись $choice удалена" 6 40
    fi
}

list_records() {
    local output=$(mktemp)
    
    echo "╔════════════════════════════════════════════════════════╗" > "$output"
    echo "║         ЛОКАЛЬНЫЕ DNS ЗАПИСИ (.local)                  ║" >> "$output"
    echo "╚════════════════════════════════════════════════════════╝" >> "$output"
    echo "" >> "$output"
    
    if [[ -f "$HOSTS_DB" && -s "$HOSTS_DB" ]]; then
        printf "%-25s %-15s %-25s\n" "HOSTNAME" "IP ADDRESS" "ОПИСАНИЕ" >> "$output"
        echo "─────────────────────────────────────────────────────────────" >> "$output"
        
        while IFS='|' read -r hostname ip description date; do
            [[ -z "$hostname" ]] && continue
            printf "%-25s %-15s %-25s\n" "$hostname" "$ip" "$description" >> "$output"
        done < "$HOSTS_DB"
        
        echo "" >> "$output"
        echo "Всего записей: $(grep -c '|' "$HOSTS_DB" || echo 0)" >> "$output"
        echo "" >> "$output"
        echo "База данных: $HOSTS_DB" >> "$output"
    else
        echo "Нет записей" >> "$output"
        echo "" >> "$output"
        echo "Используйте 'Добавить запись' или 'Сканировать сеть'" >> "$output"
    fi
    
    dialog --title "DNS Records" --textbox "$output" 25 70
    rm -f "$output"
}

export_records() {
    mkdir -p /srv/sys/backups
    
    local export_file="/srv/sys/backups/dns_export_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "# DNS Records Export - $(date)"
        echo "# Config: $DNS_CONFIG"
        echo "# Database: $HOSTS_DB"
        echo ""
        echo "=== DNSMASQ CONFIG ==="
        cat "$DNS_CONFIG"
        echo ""
        echo "=== HOSTS DATABASE ==="
        cat "$HOSTS_DB"
    } > "$export_file"
    
    dialog --msgbox "✅ Экспорт завершён:\n\n$export_file\n\nРазмер: $(du -h "$export_file" | awk '{print $1}')" 10 60
}

import_records() {
    local import_file=$(dialog --fselect /srv/sys/backups/ 14 60 3>&1 1>&2 2>&3)
    
    if [[ -n "$import_file" && -f "$import_file" ]]; then
        grep "^address=" "$import_file" >> "$DNS_CONFIG" 2>/dev/null || true
        systemctl restart dnsmasq
        dialog --msgbox "✅ Импорт завершён из:\n$import_file" 8 50
    fi
}

################################################################################
# СТАТУС И ДИАГНОСТИКА
################################################################################

show_status() {
    local service_status="❌ Остановлен"
    if systemctl is-active --quiet dnsmasq; then
        service_status="✅ Запущен"
    fi
    
    local records_count=$(grep -c "^address=" "$DNS_CONFIG" 2>/dev/null || echo "0")
    local cache_size=$(grep "cache-size" /etc/dnsmasq.conf 2>/dev/null | awk -F= '{print $2}' || echo "N/A")
    local listen_addrs=$(grep "listen-address" /etc/dnsmasq.conf 2>/dev/null | sed 's/listen-address=//' | tr '\n' ', ' || echo "N/A")
    
    local status_text=$(cat <<STATUS
╔════════════════════════════════════════════════════════╗
║             DNS SERVER STATUS                          ║
╚════════════════════════════════════════════════════════╝

🔧 Статус сервиса:
   $service_status

📊 Статистика:
   Записей: $records_count
   Размер кеша: $cache_size
   
🌐 Listen адреса:
   $listen_addrs

📡 Upstream DNS:
$(grep "^server=" /etc/dnsmasq.conf 2>/dev/null | sed 's/server=/   /' || echo "   N/A")

💾 Файлы:
   Config: /etc/dnsmasq.conf
   Local: $DNS_CONFIG
   DB: $HOSTS_DB
   Log: $LOG_FILE

📝 Последние 10 строк лога:
$(tail -n 10 "$LOG_FILE" 2>/dev/null || echo "   Логи пусты")

💡 Полезные команды:
   nslookup <hostname>.local
   dig @localhost <hostname>.local
   systemctl status dnsmasq

STATUS
)

    dialog --title "DNS Status" --msgbox "$status_text" 30 70
}

test_dns() {
    local test_host=$(dialog --inputbox "Введите hostname для проверки:\n\nПример: server1.local" 10 50 3>&1 1>&2 2>&3)
    
    if [[ -z "$test_host" ]]; then
        return
    fi
    
    local result=$(mktemp)
    
    {
        echo "╔════════════════════════════════════════════════╗"
        echo "║          DNS TEST: $test_host"
        echo "╚════════════════════════════════════════════════╝"
        echo ""
        echo "=== NSLOOKUP ==="
        nslookup "$test_host" localhost 2>&1 || echo "Не найдено"
        echo ""
        echo "=== DIG ==="
        dig "$test_host" @localhost +short 2>&1 || echo "Не найдено"
        echo ""
        echo "=== PING (1 пакет) ==="
        ping -c 1 -W 2 "$test_host" 2>&1 || echo "Недоступен"
    } > "$result"
    
    dialog --title "DNS Test" --textbox "$result" 20 70
    rm -f "$result"
}

################################################################################
# МЕНЮ
################################################################################

dns_menu() {
    mkdir -p "$(dirname $LOG_FILE)" "$(dirname $HOSTS_DB)"
    
    while true; do
        local status_icon="❌"
        local status_text="STOPPED"
        if systemctl is-active --quiet dnsmasq 2>/dev/null; then 
            status_icon="✅"
            status_text="RUNNING"
        fi
        
        local records_count=$(grep -c "^address=" "$DNS_CONFIG" 2>/dev/null || echo "0")
        
        local choice=$(dialog --clear \
            --backtitle "Local DNS Manager v2" \
            --title "$status_icon DNS Server [$status_text] | Records: $records_count" \
            --menu "Выберите действие:" \
            22 75 14 \
            1 "📥 Установить/Переустановить DNS сервер" \
            2 "➕ Добавить запись вручную" \
            3 "📋 Добавить несколько записей" \
            4 "🔍 Сканировать сеть (Auto-discover)" \
            5 "➖ Удалить запись" \
            6 "📜 Список всех записей" \
            7 "💾 Экспорт конфигурации" \
            8 "📂 Импорт конфигурации" \
            9 "📊 Статус сервера" \
            10 "🧪 Тест DNS (nslookup/dig/ping)" \
            11 "🔄 Перезапустить сервис" \
            12 "📖 Показать логи" \
            0 "◀ Назад в главное меню" \
            3>&1 1>&2 2>&3)
        
        case $choice in
            1) install_dnsmasq ;;
            2) add_dns_record ;;
            3) bulk_add_records ;;
            4) scan_network ;;
            5) remove_dns_record ;;
            6) list_records ;;
            7) export_records ;;
            8) import_records ;;
            9) show_status ;;
            10) test_dns ;;
            11) 
                systemctl restart dnsmasq 2>/dev/null || dialog --msgbox "❌ Ошибка перезапуска" 6 30
                dialog --msgbox "✅ Сервис перезапущен" 6 30
                ;;
            12)
                if [[ -f "$LOG_FILE" && -s "$LOG_FILE" ]]; then
                    dialog --textbox "$LOG_FILE" 20 70
                else
                    dialog --msgbox "Логи пусты или файл не существует" 7 40
                fi
                ;;
            0|"") return ;;
        esac
    done
}

# Запуск если скрипт вызван напрямую
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}Требуются права root${NC}"
        exit 1
    fi
    dns_menu
fi
