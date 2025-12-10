#!/bin/bash
################################################################################
# Скрипт максимального усиления безопасности сервера
# Цель: Реализация всех современных практик защиты Linux-серверов
# Автор: Sandrick Tech
# Версия: 5.0 Enhanced Security Edition
################################################################################

# Строгий режим выполнения
set -euo pipefail

################################################################################
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
################################################################################

# Цветовая палитра для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Пути к конфигурационным файлам
SSH_CONFIG="/etc/ssh/sshd_config"              # Конфигурация SSH-сервера
SSH_PORT=2222                                   # Нестандартный порт SSH (вместо 22)
FAIL2BAN_CONFIG="/etc/fail2ban/jail.local"     # Локальная конфигурация fail2ban
IPTABLES_CONFIG="/etc/iptables/rules.v4"           # Конфигурация firewall iptables
AUDIT_RULES="/etc/audit/rules.d/audit.rules"   # Правила аудита системы
BACKUP_DIR="/root/backups/security"             # Директория для backup конфигов

# Логирование
LOG_FILE="/var/log/security-hardening.log"     # Лог действий скрипта

################################################################################
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
################################################################################

###
# Функция: log_message
# Описание: Запись сообщения в лог с временной меткой
# Параметры:
#   $1 - уровень (INFO/WARN/ERROR)
#   $2 - сообщение
###
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Запись в лог-файл с форматом: [timestamp] [LEVEL] message
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    
    # Вывод в консоль с цветом в зависимости от уровня
    case $level in
        INFO)  echo -e "${GREEN}[INFO]${NC} $message" ;;
        WARN)  echo -e "${YELLOW}[WARN]${NC} $message" ;;
        ERROR) echo -e "${RED}[ERROR]${NC} $message" ;;
        STEP)  echo -e "${MAGENTA}[STEP]${NC} $message" ;;
    esac
}

###
# Функция: backup_config
# Описание: Создание резервной копии конфигурационного файла
# Параметры:
#   $1 - путь к файлу для backup
###
backup_config() {
    local file="$1"
    # Проверяем существование файла
    if [[ -f "$file" ]]; then
        local backup_name="$(basename "$file").backup_$(date +%Y%m%d_%H%M%S)"
        # Создаём директорию для backup если не существует
        mkdir -p "$BACKUP_DIR"
        # Копируем файл с сохранением атрибутов (-a)
        cp -a "$file" "$BACKUP_DIR/$backup_name"
        log_message "INFO" "Backup создан: $BACKUP_DIR/$backup_name"
    else
        log_message "WARN" "Файл не найден для backup: $file"
    fi
}

###
# Функция: check_root
# Описание: Проверка запуска от root
###
check_root() {
    # $EUID - Effective User ID, для root = 0
    if [ "$EUID" -ne 0 ]; then
        log_message "ERROR" "Скрипт должен быть запущен от root"
        echo "Используйте: sudo $0"
        exit 1
    fi
}

################################################################################
# SSH HARDENING - УСИЛЕНИЕ SSH
################################################################################

###
# Функция: configure_ssh_hardening
# Описание: Максимальное усиление безопасности SSH
# Включает:
#   - Изменение порта на нестандартный (2222)
#   - Отключение root login
#   - Отключение паролей (только ключи)
#   - Ограничение пользователей
#   - Таймауты для idle соединений
#   - Защита от брутфорса
###
configure_ssh_hardening() {
    log_message "STEP" "Настройка усиленной защиты SSH..."
    
    # Создаём backup текущей конфигурации
    backup_config "$SSH_CONFIG"
    
    # Временный файл для новой конфигурации
    local temp_config="/tmp/sshd_config.tmp"
    
    # Создаём новую конфигурацию SSH с максимальной безопасностью
    cat > "$temp_config" << 'EOF'
# SSH Configuration - Maximum Security
# Generated by security-hardening-advanced.sh

# Базовые настройки
Port 2222                                    # Нестандартный порт (защита от автосканеров)
Protocol 2                                   # Только SSH версии 2 (версия 1 небезопасна)
AddressFamily inet                           # Только IPv4 (отключаем IPv6 если не используется)

# Аутентификация
PermitRootLogin no                           # ЗАПРЕТ входа под root
PasswordAuthentication no                    # ЗАПРЕТ аутентификации по паролю
PubkeyAuthentication yes                     # ТОЛЬКО аутентификация по SSH-ключам
ChallengeResponseAuthentication no           # Отключаем challenge-response
UsePAM yes                                   # Используем PAM для дополнительных проверок
AuthenticationMethods publickey              # Явно указываем метод аутентификации

# Ограничения пользователей
AllowUsers gate                              # Разрешён вход ТОЛЬКО для gate (добавьте других через пробел)
DenyUsers root admin administrator           # Явный запрет для опасных имён
MaxAuthTries 3                               # Максимум 3 попытки аутентификации
MaxSessions 2                                # Максимум 2 одновременных сессии на соединение
MaxStartups 2:50:10                          # Ограничение одновременных неаутентифицированных соединений

# Таймауты и keepalive
LoginGraceTime 30                            # 30 секунд на вход (по умолчанию 120)
ClientAliveInterval 300                      # Проверка клиента каждые 5 минут
ClientAliveCountMax 2                        # После 2 неудачных проверок - разрыв

# Защита от брутфорса
PermitEmptyPasswords no                      # Запрет пустых паролей
StrictModes yes                              # Проверка прав на домашнюю директорию и ключи

# X11 и переадресация
X11Forwarding no                             # Отключаем X11 forwarding (не нужен на сервере)
AllowTcpForwarding yes                       # Разрешаем TCP forwarding (нужен для ProxyJump)
AllowAgentForwarding yes                     # Разрешаем agent forwarding (нужен для ProxyJump)
PermitTunnel no                              # Запрет туннелирования
GatewayPorts no                              # Запрет remote port forwarding

# Логирование
SyslogFacility AUTH                          # Логирование в AUTH facility
LogLevel VERBOSE                             # Подробное логирование (для fail2ban)

# Криптография (только сильные алгоритмы)
# Отключаем слабые и устаревшие алгоритмы
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group-exchange-sha256
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512,hmac-sha2-256

# Дополнительные ограничения
PermitUserEnvironment no                     # Запрет изменения окружения пользователем
Compression no                               # Отключаем компрессию (защита от атак)
UseDNS no                                    # Отключаем DNS lookup (ускоряет подключение)
PrintMotd no                                 # MOTD выводим через /etc/profile.d/
PrintLastLog yes                             # Показываем время последнего входа

# Subsystems
Subsystem sftp /usr/lib/openssh/sftp-server  # SFTP для передачи файлов

# Banner
Banner /etc/ssh/ssh_banner.txt               # Предупреждающий баннер
EOF

    # Заменяем конфигурацию
    mv "$temp_config" "$SSH_CONFIG"
    chmod 644 "$SSH_CONFIG"
    
    # Создаём warning banner для SSH
    cat > /etc/ssh/ssh_banner.txt << 'EOF'
***************************************************************************
                           ВНИМАНИЕ! WARNING!
***************************************************************************
Это частная система. Несанкционированный доступ запрещён.
This is a private system. Unauthorized access is prohibited.

Все действия логируются и мониторятся.
All actions are logged and monitored.

Нарушители будут преследоваться по закону.
Violators will be prosecuted to the fullest extent of the law.
***************************************************************************
EOF

    # Проверяем конфигурацию SSH
    if sshd -t; then
        log_message "INFO" "✅ Конфигурация SSH корректна"
        
        # Перезапускаем SSH
        systemctl restart sshd
        log_message "INFO" "✅ SSH перезапущен на порту $SSH_PORT"
        
        echo ""
        echo -e "${YELLOW}╔════════════════════════════════════════════════════════╗${NC}"
        echo -e "${YELLOW}║  ⚠️  ВНИМАНИЕ! SSH порт изменён на $SSH_PORT            ║${NC}"
        echo -e "${YELLOW}║                                                        ║${NC}"
        echo -e "${YELLOW}║  Для подключения используйте:                         ║${NC}"
        echo -e "${YELLOW}║  ssh -p $SSH_PORT gate@server                          ║${NC}"
        echo -e "${YELLOW}║                                                        ║${NC}"
        echo -e "${YELLOW}║  НЕ ЗАКРЫВАЙТЕ текущую SSH-сессию!                    ║${NC}"
        echo -e "${YELLOW}║  Проверьте подключение в НОВОМ окне терминала!        ║${NC}"
        echo -e "${YELLOW}╚════════════════════════════════════════════════════════╝${NC}"
        echo ""
    else
        log_message "ERROR" "❌ Ошибка в конфигурации SSH!"
        # Восстанавливаем из backup
        local latest_backup=$(ls -t "$BACKUP_DIR"/sshd_config.backup_* | head -1)
        cp "$latest_backup" "$SSH_CONFIG"
        log_message "INFO" "Конфигурация восстановлена из backup"
        return 1
    fi
}

################################################################################
# FAIL2BAN - ЗАЩИТА ОТ БРУТФОРСА
################################################################################

###
# Функция: install_fail2ban
# Описание: Установка и настройка fail2ban для защиты от брутфорс-атак
# Fail2ban автоматически блокирует IP после нескольких неудачных попыток входа
###
install_fail2ban() {
    log_message "STEP" "Установка и настройка fail2ban..."
    
    # Проверяем, установлен ли fail2ban
    if ! command -v fail2ban-client &> /dev/null; then
        log_message "INFO" "Установка fail2ban..."
        apt-get update -qq
        apt-get install -y fail2ban
    else
        log_message "INFO" "fail2ban уже установлен"
    fi
    
    # Создаём локальную конфигурацию
    backup_config "$FAIL2BAN_CONFIG"
    
    cat > "$FAIL2BAN_CONFIG" << EOF
# Fail2ban Local Configuration
# Maximum Security Setup

[DEFAULT]
# Ban настройки по умолчанию
bantime = 3600                    # Время блокировки: 1 час (3600 секунд)
findtime = 600                    # Период отслеживания: 10 минут
maxretry = 3                      # Максимум попыток: 3
destemail = root@localhost        # Email для уведомлений
sender = fail2ban@localhost       # Отправитель уведомлений
action = %(action_mwl)s           # Действие: ban + email с логами

# SSH Protection - Защита SSH
[sshd]
enabled = true                    # Включить защиту SSH
port = $SSH_PORT                  # Порт SSH (наш нестандартный)
filter = sshd                     # Фильтр для анализа логов
logpath = /var/log/auth.log       # Путь к логу аутентификации
maxretry = 3                      # 3 попытки входа
bantime = 7200                    # Ban на 2 часа
findtime = 600                    # Период 10 минут

# SSH DDoS Protection - Защита от SSH DDoS
[sshd-ddos]
enabled = true
port = $SSH_PORT
filter = sshd-ddos
logpath = /var/log/auth.log
maxretry = 10                     # 10 подключений
bantime = 3600                    # Ban на 1 час
findtime = 60                     # За 1 минуту

# Recidive - Повторные нарушители (перманентный ban)
[recidive]
enabled = true
filter = recidive
logpath = /var/log/fail2ban.log
action = %(action_mwl)s
bantime = 604800                  # Ban на неделю (7 дней)
findtime = 86400                  # Период 24 часа
maxretry = 3                      # После 3 повторных нарушений
EOF

    # Создаём фильтр для SSH DDoS
    cat > /etc/fail2ban/filter.d/sshd-ddos.conf << 'EOF'
# Fail2ban filter for SSH DDoS
[Definition]
failregex = ^.*sshd.*: Connection from <HOST>.*$
ignoreregex =
EOF

    # Перезапускаем fail2ban
    systemctl enable fail2ban
    systemctl restart fail2ban
    
    log_message "INFO" "✅ fail2ban настроен и запущен"
    
    # Показываем статус
    echo ""
    log_message "INFO" "Статус fail2ban jails:"
    fail2ban-client status
}

################################################################################
# IPTABLES FIREWALL - НАСТРОЙКА МЕЖСЕТЕВОГО ЭКРАНА
################################################################################

###
# Функция: configure_iptables_firewall
# Описание: Настройка iptables с правилами по умолчанию
# Политика: DROP all по умолчанию, разрешаем только необходимое
###
configure_iptables_firewall() {
    log_message "STEP" "Настройка iptables Firewall..."
    
    # Устанавливаем iptables-persistent для сохранения правил
    apt-get install -y iptables iptables-persistent
    
    # Очищаем все правила
    iptables -F
    iptables -X
    iptables -t nat -F
    iptables -t nat -X
    iptables -t mangle -F
    iptables -t mangle -X
    log_message "INFO" "Очистка существующих правил"
    
    # Устанавливаем политики по умолчанию
    iptables -P INPUT DROP
    iptables -P FORWARD DROP
    iptables -P OUTPUT ACCEPT
    log_message "INFO" "Политика по умолчанию: DROP INPUT/FORWARD, ACCEPT OUTPUT"
    
    # Разрешаем loopback
    iptables -A INPUT -i lo -j ACCEPT
    iptables -A OUTPUT -o lo -j ACCEPT
    log_message "INFO" "Loopback интерфейс разрешён"
    
    # Разрешаем установленные соединения
    iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
    log_message "INFO" "Разрешены ESTABLISHED/RELATED соединения"
    
    # Разрешаем SSH на нестандартном порту
    iptables -A INPUT -p tcp --dport "$SSH_PORT" -j ACCEPT
    log_message "INFO" "Разрешён SSH на порту $SSH_PORT"
    
    # Rate limiting для SSH (защита от брутфорса)
    # Ограничивает 6 подключений в 30 секунд с одного IP
    iptables -A INPUT -p tcp --dport "$SSH_PORT" -m conntrack --ctstate NEW -m recent --set
    iptables -A INPUT -p tcp --dport "$SSH_PORT" -m conntrack --ctstate NEW -m recent --update --seconds 30 --hitcount 6 -j DROP
    log_message "INFO" "Rate limiting для SSH активирован (6 conn/30sec)"
    
    # Защита от типичных атак
    # Блокируем invalid пакеты
    iptables -A INPUT -m conntrack --ctstate INVALID -j DROP
    log_message "INFO" "Блокировка INVALID пакетов"
    
    # Защита от SYN flood
    iptables -A INPUT -p tcp --syn -m limit --limit 1/s --limit-burst 3 -j ACCEPT
    iptables -A INPUT -p tcp --syn -j DROP
    log_message "INFO" "Защита от SYN flood"
    
    # Разрешаем ICMP (ping) с ограничением
    iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/s -j ACCEPT
    iptables -A INPUT -p icmp --icmp-type echo-request -j DROP
    log_message "INFO" "Ping разрешён с rate limit"
    
    # Логирование заблокированных пакетов
    iptables -A INPUT -m limit --limit 5/min -j LOG --log-prefix "iptables-dropped: " --log-level 7
    
    # Сохраняем правила
    mkdir -p /etc/iptables
    iptables-save > /etc/iptables/rules.v4
    log_message "INFO" "Правила сохранены в /etc/iptables/rules.v4"
    
    # Создаём systemd service для автозагрузки
    cat > /etc/systemd/system/iptables-restore.service <<EOF
[Unit]
Description=Restore iptables rules
Before=network-pre.target
Wants=network-pre.target

[Service]
Type=oneshot
ExecStart=/sbin/iptables-restore /etc/iptables/rules.v4
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable iptables-restore.service
    
    log_message "INFO" "✅ iptables Firewall активирован"
    
    # Показываем статус
    echo ""
    log_message "INFO" "Статус iptables:"
    iptables -L -v -n --line-numbers | head -20
}

################################################################################
# ДВУХФАКТОРНАЯ АУТЕНТИФИКАЦИЯ (2FA)
################################################################################

###
# Функция: setup_2fa
# Описание: Настройка двухфакторной аутентификации через Google Authenticator
# Добавляет второй фактор аутентификации (TOTP) для SSH
###
setup_2fa() {
    log_message "STEP" "Настройка двухфакторной аутентификации (2FA)..."
    
    # Устанавливаем Google Authenticator PAM module
    if ! dpkg -l | grep -q libpam-google-authenticator; then
        log_message "INFO" "Установка libpam-google-authenticator..."
        apt-get install -y libpam-google-authenticator
    fi
    
    # Настраиваем PAM для SSH
    backup_config "/etc/pam.d/sshd"
    
    # Добавляем Google Authenticator в PAM конфигурацию
    # Комментируем стандартную PAM аутентификацию
    sed -i 's/^@include common-auth/#@include common-auth/' /etc/pam.d/sshd
    
    # Добавляем Google Authenticator в начало файла
    sed -i '1i auth required pam_google_authenticator.so nullok' /etc/pam.d/sshd
    sed -i '2i auth required pam_permit.so' /etc/pam.d/sshd
    
    # Настраиваем SSH для использования 2FA
    backup_config "$SSH_CONFIG"
    
    # Включаем ChallengeResponseAuthentication для 2FA
    sed -i 's/^ChallengeResponseAuthentication no/ChallengeResponseAuthentication yes/' "$SSH_CONFIG"
    
    # Добавляем метод аутентификации: publickey + keyboard-interactive (2FA)
    if grep -q "^AuthenticationMethods" "$SSH_CONFIG"; then
        sed -i 's/^AuthenticationMethods.*/AuthenticationMethods publickey,keyboard-interactive/' "$SSH_CONFIG"
    else
        echo "AuthenticationMethods publickey,keyboard-interactive" >> "$SSH_CONFIG"
    fi
    
    # Проверяем конфигурацию и перезапускаем SSH
    if sshd -t; then
        systemctl restart sshd
        log_message "INFO" "✅ 2FA настроен в SSH"
    else
        log_message "ERROR" "Ошибка конфигурации SSH при настройке 2FA"
        return 1
    fi
    
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  Двухфакторная аутентификация настроена                   ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Для активации 2FA для каждого пользователя выполните:"
    echo "  1. Войдите под пользователем: su - username"
    echo "  2. Запустите: google-authenticator"
    echo "  3. Ответьте на вопросы (рекомендуется: y, y, y, n, y)"
    echo "  4. Отсканируйте QR-код в Google Authenticator app"
    echo "  5. Сохраните emergency scratch codes в безопасное место!"
    echo ""
    echo "После этого для входа потребуется:"
    echo "  1. SSH-ключ"
    echo "  2. Verification code из Google Authenticator"
    echo ""
}

################################################################################
# СИСТЕМЫ ОБНАРУЖЕНИЯ ВТОРЖЕНИЙ (IDS)
################################################################################

###
# Функция: install_ids_tools
# Описание: Установка инструментов обнаружения вторжений и руткитов
# Включает: rkhunter, chkrootkit, AIDE
###
install_ids_tools() {
    log_message "STEP" "Установка систем обнаружения вторжений..."
    
    # rkhunter - Rootkit Hunter (поиск руткитов)
    if ! command -v rkhunter &> /dev/null; then
        log_message "INFO" "Установка rkhunter..."
        apt-get install -y rkhunter
        
        # Обновляем базу данных rkhunter
        rkhunter --update
        rkhunter --propupd
        
        log_message "INFO" "✅ rkhunter установлен"
    fi
    
    # chkrootkit - Проверка на руткиты
    if ! command -v chkrootkit &> /dev/null; then
        log_message "INFO" "Установка chkrootkit..."
        apt-get install -y chkrootkit
        log_message "INFO" "✅ chkrootkit установлен"
    fi
    
    # AIDE - Advanced Intrusion Detection Environment (контроль целостности файлов)
    if ! command -v aide &> /dev/null; then
        log_message "INFO" "Установка AIDE..."
        apt-get install -y aide aide-common
        
        # Инициализируем базу данных AIDE (может занять несколько минут)
        log_message "INFO" "Инициализация базы данных AIDE (это может занять время)..."
        aideinit
        
        # Копируем новую базу данных
        if [ -f /var/lib/aide/aide.db.new ]; then
            cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db
        fi
        
        log_message "INFO" "✅ AIDE установлен и инициализирован"
    fi
    
    # Настраиваем cron для автоматических проверок
    log_message "INFO" "Настройка автоматических проверок безопасности..."
    
    # rkhunter - ежедневная проверка
    cat > /etc/cron.daily/rkhunter-check << 'EOF'
#!/bin/bash
# Ежедневная проверка rkhunter
/usr/bin/rkhunter --cronjob --update --quiet
EOF
    chmod +x /etc/cron.daily/rkhunter-check
    
    # AIDE - еженедельная проверка
    cat > /etc/cron.weekly/aide-check << 'EOF'
#!/bin/bash
# Еженедельная проверка целостности AIDE
/usr/bin/aide --check | mail -s "AIDE Report for $(hostname)" root
EOF
    chmod +x /etc/cron.weekly/aide-check
    
    log_message "INFO" "✅ Автоматические проверки настроены"
    log_message "INFO" "  - rkhunter: ежедневно"
    log_message "INFO" "  - AIDE: еженедельно"
}

################################################################################
# СИСТЕМА АУДИТА (AUDITD)
################################################################################

###
# Функция: configure_auditd
# Описание: Настройка auditd для логирования всех действий пользователей
# Логирует: изменения файлов, выполнение команд, сетевую активность
###
configure_auditd() {
    log_message "STEP" "Настройка системы аудита (auditd)..."
    
    # Устанавливаем auditd
    if ! command -v auditctl &> /dev/null; then
        log_message "INFO" "Установка auditd..."
        apt-get install -y auditd audispd-plugins
    fi
    
    # Создаём правила аудита
    backup_config "$AUDIT_RULES"
    
    cat > "$AUDIT_RULES" << 'EOF'
# Audit Rules for Maximum Security
# Generated by security-hardening-advanced.sh

# Удаляем все предыдущие правила
-D

# Увеличиваем буфер для логов
-b 8192

# Делаем конфигурацию неизменяемой (можно изменить только после перезагрузки)
# Раскомментируйте для максимальной защиты:
# -e 2

## МОНИТОРИНГ ИЗМЕНЕНИЙ СИСТЕМНЫХ ФАЙЛОВ

# Мониторинг /etc/passwd и /etc/group (изменения пользователей/групп)
-w /etc/passwd -p wa -k identity
-w /etc/group -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/gshadow -p wa -k identity

# Мониторинг sudo конфигурации
-w /etc/sudoers -p wa -k sudoers
-w /etc/sudoers.d/ -p wa -k sudoers

# Мониторинг SSH конфигурации
-w /etc/ssh/sshd_config -p wa -k sshd_config

# Мониторинг изменений cron
-w /etc/cron.allow -p wa -k cron
-w /etc/cron.deny -p wa -k cron
-w /etc/cron.d/ -p wa -k cron
-w /etc/cron.daily/ -p wa -k cron
-w /etc/cron.hourly/ -p wa -k cron
-w /etc/cron.monthly/ -p wa -k cron
-w /etc/cron.weekly/ -p wa -k cron
-w /etc/crontab -p wa -k cron

# Мониторинг systemd
-w /etc/systemd/ -p wa -k systemd
-w /lib/systemd/ -p wa -k systemd

## МОНИТОРИНГ СЕТЕВОЙ АКТИВНОСТИ

# Мониторинг изменений сетевых настроек
-w /etc/hosts -p wa -k network
-w /etc/network/ -p wa -k network
-w /etc/netplan/ -p wa -k network

# Мониторинг firewall изменений
-w /etc/iptables/ -p wa -k firewall
-w /etc/iptables/rules.v4 -p wa -k firewall

## МОНИТОРИНГ ПРИВИЛЕГИРОВАННЫХ КОМАНД

# Логирование использования sudo
-a always,exit -F arch=b64 -S execve -F euid=0 -F auid>=1000 -F auid!=-1 -k privileged_commands
-a always,exit -F arch=b32 -S execve -F euid=0 -F auid>=1000 -F auid!=-1 -k privileged_commands

# Логирование изменений прав доступа
-a always,exit -F arch=b64 -S chmod,fchmod,fchmodat -F auid>=1000 -F auid!=-1 -k perm_mod
-a always,exit -F arch=b32 -S chmod,fchmod,fchmodat -F auid>=1000 -F auid!=-1 -k perm_mod

# Логирование изменений владельца файлов
-a always,exit -F arch=b64 -S chown,fchown,fchownat,lchown -F auid>=1000 -F auid!=-1 -k perm_mod
-a always,exit -F arch=b32 -S chown,fchown,fchownat,lchown -F auid>=1000 -F auid!=-1 -k perm_mod

## МОНИТОРИНГ ПОПЫТОК НЕСАНКЦИОНИРОВАННОГО ДОСТУПА

# Логирование неудачных попыток доступа к файлам
-a always,exit -F arch=b64 -S open,openat -F exit=-EACCES -F auid>=1000 -F auid!=-1 -k access_denied
-a always,exit -F arch=b64 -S open,openat -F exit=-EPERM -F auid>=1000 -F auid!=-1 -k access_denied

## МОНИТОРИНГ ЗАГРУЗКИ KERNEL MODULES

# Логирование загрузки/выгрузки модулей ядра
-w /sbin/insmod -p x -k modules
-w /sbin/rmmod -p x -k modules
-w /sbin/modprobe -p x -k modules
-a always,exit -F arch=b64 -S init_module,delete_module -k modules

## МОНИТОРИНГ МОНТИРОВАНИЯ

# Логирование операций монтирования
-a always,exit -F arch=b64 -S mount,umount2 -F auid>=1000 -F auid!=-1 -k mount

## МОНИТОРИНГ УДАЛЕНИЯ ФАЙЛОВ

# Логирование удаления файлов
-a always,exit -F arch=b64 -S unlink,unlinkat,rename,renameat -F auid>=1000 -F auid!=-1 -k delete
EOF

    # Перезагружаем правила auditd
    augenrules --load
    
    # Включаем и запускаем auditd
    systemctl enable auditd
    systemctl restart auditd
    
    log_message "INFO" "✅ Система аудита (auditd) настроена и запущена"
    
    echo ""
    log_message "INFO" "Просмотр логов аудита:"
    echo "  ausearch -k identity     # Изменения пользователей"
    echo "  ausearch -k sshd_config  # Изменения SSH"
    echo "  ausearch -k privileged_commands  # Команды с sudo"
    echo "  aureport                 # Сводный отчёт"
}

################################################################################
# АВТОМАТИЧЕСКИЕ ОБНОВЛЕНИЯ БЕЗОПАСНОСТИ
################################################################################

###
# Функция: enable_auto_updates
# Описание: Включение автоматических обновлений безопасности
# Только security updates устанавливаются автоматически
###
enable_auto_updates() {
    log_message "STEP" "Настройка автоматических обновлений безопасности..."
    
    # Устанавливаем unattended-upgrades
    if ! dpkg -l | grep -q unattended-upgrades; then
        apt-get install -y unattended-upgrades apt-listchanges
    fi
    
    # Настраиваем автоматические обновления только для security
    cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
// Automatic Security Updates Configuration

Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};

// Список пакетов которые НЕ обновлять автоматически
Unattended-Upgrade::Package-Blacklist {
};

// Автоматически перезагружать если требуется (например, kernel update)
Unattended-Upgrade::Automatic-Reboot "false";

// Если включена автоперезагрузка, время перезагрузки
Unattended-Upgrade::Automatic-Reboot-Time "02:00";

// Удалять неиспользуемые зависимости
Unattended-Upgrade::Remove-Unused-Dependencies "true";

// Email уведомления
Unattended-Upgrade::Mail "root";
Unattended-Upgrade::MailReport "on-change";
EOF

    # Включаем автоматические обновления
    cat > /etc/apt/apt.conf.d/20auto-upgrades << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
EOF

    # Проверяем конфигурацию
    unattended-upgrades --dry-run --debug
    
    log_message "INFO" "✅ Автоматические обновления безопасности включены"
}

################################################################################
# ДОПОЛНИТЕЛЬНЫЕ УЛУЧШЕНИЯ БЕЗОПАСНОСТИ
################################################################################

###
# Функция: kernel_hardening
# Описание: Усиление безопасности на уровне ядра через sysctl
###
kernel_hardening() {
    log_message "STEP" "Усиление безопасности ядра (sysctl)..."
    
    backup_config "/etc/sysctl.conf"
    
    cat >> /etc/sysctl.conf << 'EOF'

# Kernel Security Hardening
# Added by security-hardening-advanced.sh

# Защита от IP spoofing
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Игнорировать ICMP redirects (защита от MITM)
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.default.secure_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv6.conf.default.accept_redirects = 0

# Не отправлять ICMP redirects
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0

# Игнорировать ping (необязательно)
# net.ipv4.icmp_echo_ignore_all = 1

# Защита от SYN flood атак
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 5

# Логирование подозрительных пакетов
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.default.log_martians = 1

# Игнорировать broadcast ping
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Игнорировать bogus ICMP errors
net.ipv4.icmp_ignore_bogus_error_responses = 1

# Отключить IPv6 если не используется
# net.ipv6.conf.all.disable_ipv6 = 1
# net.ipv6.conf.default.disable_ipv6 = 1
# net.ipv6.conf.lo.disable_ipv6 = 1

# Защита от переполнения буфера
kernel.exec-shield = 1
kernel.randomize_va_space = 2

# Ограничение доступа к dmesg
kernel.dmesg_restrict = 1

# Ограничение доступа к kernel pointers
kernel.kptr_restrict = 2

# Защита от ptrace (debugging) других процессов
kernel.yama.ptrace_scope = 1
EOF

    # Применяем изменения
    sysctl -p
    
    log_message "INFO" "✅ Параметры безопасности ядра применены"
}

###
# Функция: disable_unnecessary_services
# Описание: Отключение ненужных служб для уменьшения поверхности атаки
###
disable_unnecessary_services() {
    log_message "STEP" "Отключение ненужных служб..."
    
    # Список потенциально ненужных служб
    local services=(
        "avahi-daemon"      # Zeroconf/Bonjour (обычно не нужен на сервере)
        "cups"              # Печать (не нужно на сервере)
        "bluetooth"         # Bluetooth (не нужно на сервере)
        "iscsid"            # iSCSI (если не используется SAN)
    )
    
    for service in "${services[@]}"; do
        if systemctl is-enabled "$service" &>/dev/null; then
            systemctl stop "$service"
            systemctl disable "$service"
            log_message "INFO" "Отключена служба: $service"
        fi
    done
    
    log_message "INFO" "✅ Ненужные службы отключены"
}

################################################################################
# ГЛАВНАЯ ФУНКЦИЯ
################################################################################

###
# Функция: main
# Описание: Главная функция - выполняет все шаги усиления безопасности
###
main() {
    # Проверка root
    check_root
    
    # Создаём лог-файл
    touch "$LOG_FILE"
    chmod 600 "$LOG_FILE"
    
    echo -e "${CYAN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        МАКСИМАЛЬНОЕ УСИЛЕНИЕ БЕЗОПАСНОСТИ СЕРВЕРА                ║
║                 Security Hardening Script v5.0                   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    log_message "INFO" "Начало процесса усиления безопасности..."
    
    # Выполняем все шаги
    configure_ssh_hardening
    echo ""
    
    install_fail2ban
    echo ""
    
    configure_iptables_firewall
    echo ""
    
    setup_2fa
    echo ""
    
    install_ids_tools
    echo ""
    
    configure_auditd
    echo ""
    
    enable_auto_updates
    echo ""
    
    kernel_hardening
    echo ""
    
    disable_unnecessary_services
    echo ""
    
    # Финальное сообщение
    echo -e "${GREEN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║             ✅ УСИЛЕНИЕ БЕЗОПАСНОСТИ ЗАВЕРШЕНО! ✅                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    echo "📊 СТАТИСТИКА:"
    echo "  ✅ SSH усилен (порт $SSH_PORT, только ключи, 2FA)"
    echo "  ✅ fail2ban установлен и настроен"
    echo "  ✅ iptables firewall активирован"
    echo "  ✅ Двухфакторная аутентификация настроена"
    echo "  ✅ IDS установлены (rkhunter, chkrootkit, AIDE)"
    echo "  ✅ Система аудита (auditd) запущена"
    echo "  ✅ Автоматические обновления безопасности включены"
    echo "  ✅ Ядро усилено (sysctl)"
    echo "  ✅ Ненужные службы отключены"
    echo ""
    echo "📝 ВАЖНО!"
    echo "  1. НЕ ЗАКРЫВАЙТЕ текущую SSH-сессию"
    echo "  2. Проверьте подключение в новом окне: ssh -p $SSH_PORT gate@server"
    echo "  3. Настройте 2FA для пользователей: google-authenticator"
    echo "  4. Проверьте iptables правила: iptables -L -v -n"
    echo "  5. Все изменения залогированы в: $LOG_FILE"
    echo ""
    echo "🔒 Ваш сервер теперь максимально защищён!"
    
    log_message "INFO" "Процесс усиления безопасности завершён успешно"
}

# Запуск главной функции
main "$@"
