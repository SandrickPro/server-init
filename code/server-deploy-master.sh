#!/usr/bin/env bash
#
# SERVER DEPLOYMENT MASTER
# Unified server initialization and service deployment system
# Version: 3.0
# Date: 2025-12-08
#
set -euo pipefail
IFS=$'\n\t'

# ==================== CONFIGURATION ====================
VERSION="3.0"
BASE="/srv/sys"
HOME_BASE="/srv/home"
DEPLOY_LOG="/var/log/server-deploy-master.log"
STATE_FILE="$BASE/.deployment_state.json"

# Colors
RED='\e[1;31m'
GREEN='\e[1;32m'
YELLOW='\e[1;33m'
BLUE='\e[1;34m'
MAGENTA='\e[1;35m'
CYAN='\e[1;36m'
RESET='\e[0m'

# ==================== LOGGING ====================
log() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$DEPLOY_LOG"; }
info() { echo -e "${GREEN}[✓]${RESET} $*" | tee -a "$DEPLOY_LOG"; }
warn() { echo -e "${YELLOW}[!]${RESET} $*" | tee -a "$DEPLOY_LOG"; }
error() { echo -e "${RED}[✗]${RESET} $*" | tee -a "$DEPLOY_LOG"; }
step() { echo -e "\n${CYAN}═══ $* ═══${RESET}\n" | tee -a "$DEPLOY_LOG"; }
banner() {
    echo -e "${MAGENTA}"
    cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║           SERVER DEPLOYMENT MASTER v3.0                        ║
║      Комплексная система развёртывания серверов               ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${RESET}"
}

# ==================== ROOT CHECK ====================
if [[ $EUID -ne 0 ]]; then
    error "Требуются права root. Используйте: sudo $0"
    exit 1
fi

# ==================== INITIAL SETUP ====================
mkdir -p "$BASE" "$HOME_BASE" "$(dirname "$DEPLOY_LOG")"
touch "$DEPLOY_LOG"
chmod 600 "$DEPLOY_LOG"

# ==================== STATE MANAGEMENT ====================
save_state() {
    local key="$1"
    local value="$2"
    mkdir -p "$(dirname "$STATE_FILE")"
    if [[ ! -f "$STATE_FILE" ]]; then
        echo "{}" > "$STATE_FILE"
    fi
    # Simple key-value storage
    grep -v "\"$key\":" "$STATE_FILE" > "$STATE_FILE.tmp" 2>/dev/null || echo "{}" > "$STATE_FILE.tmp"
    sed 's/}$//' "$STATE_FILE.tmp" > "$STATE_FILE.tmp2"
    echo "  \"$key\": \"$value\"" >> "$STATE_FILE.tmp2"
    echo "}" >> "$STATE_FILE.tmp2"
    mv "$STATE_FILE.tmp2" "$STATE_FILE"
    rm -f "$STATE_FILE.tmp"
}

get_state() {
    local key="$1"
    [[ -f "$STATE_FILE" ]] || return 1
    grep "\"$key\":" "$STATE_FILE" | cut -d'"' -f4 || return 1
}

# ==================== SYSTEM UPDATE ====================
system_update() {
    step "Обновление системы"
    
    info "Обновление списка пакетов..."
    apt-get update -qq
    
    info "Обновление установленных пакетов..."
    DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -qq
    
    info "Обновление до новых версий пакетов..."
    DEBIAN_FRONTEND=noninteractive apt-get dist-upgrade -y -qq
    
    info "Очистка неиспользуемых пакетов..."
    apt-get autoremove -y -qq
    apt-get autoclean -qq
    
    save_state "system_updated" "$(date +%s)"
    info "Система обновлена"
}

kernel_update() {
    step "Обновление ядра"
    
    read -p "Обновить ядро до последней версии? [y/N]: " response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        warn "Обновление ядра пропущено"
        return
    fi
    
    info "Установка последнего ядра..."
    DEBIAN_FRONTEND=noninteractive apt-get install -y linux-image-generic linux-headers-generic
    
    save_state "kernel_updated" "$(date +%s)"
    warn "Для применения нового ядра требуется перезагрузка!"
    
    read -p "Перезагрузить сейчас? [y/N]: " reboot_now
    if [[ "$reboot_now" =~ ^[Yy]$ ]]; then
        info "Перезагрузка через 5 секунд..."
        sleep 5
        reboot
    fi
}

# ==================== TIMEZONE & LOCALE ====================
setup_timezone() {
    step "Настройка временной зоны"
    
    echo "Текущая временная зона: $(timedatectl | grep "Time zone" | awk '{print $3}')"
    echo ""
    echo "Популярные временные зоны:"
    echo "  1) Europe/Moscow"
    echo "  2) Europe/London"
    echo "  3) America/New_York"
    echo "  4) Asia/Tokyo"
    echo "  5) UTC"
    echo "  6) Другая (ввести вручную)"
    echo ""
    
    read -p "Выберите вариант [1-6]: " tz_choice
    
    case $tz_choice in
        1) TIMEZONE="Europe/Moscow" ;;
        2) TIMEZONE="Europe/London" ;;
        3) TIMEZONE="America/New_York" ;;
        4) TIMEZONE="Asia/Tokyo" ;;
        5) TIMEZONE="UTC" ;;
        6) 
            read -p "Введите временную зону (например, Europe/Berlin): " TIMEZONE
            ;;
        *) TIMEZONE="UTC" ;;
    esac
    
    timedatectl set-timezone "$TIMEZONE"
    save_state "timezone" "$TIMEZONE"
    info "Временная зона установлена: $TIMEZONE"
}

setup_locale() {
    step "Настройка локали"
    
    echo "Доступные локали:"
    echo "  1) en_US.UTF-8 (English)"
    echo "  2) ru_RU.UTF-8 (Russian)"
    echo "  3) de_DE.UTF-8 (German)"
    echo "  4) Другая"
    echo ""
    
    read -p "Выберите локаль [1-4]: " locale_choice
    
    case $locale_choice in
        1) LOCALE="en_US.UTF-8" ;;
        2) LOCALE="ru_RU.UTF-8" ;;
        3) LOCALE="de_DE.UTF-8" ;;
        4)
            read -p "Введите локаль: " LOCALE
            ;;
        *) LOCALE="en_US.UTF-8" ;;
    esac
    
    locale-gen "$LOCALE"
    update-locale LANG="$LOCALE"
    
    save_state "locale" "$LOCALE"
    info "Локаль установлена: $LOCALE"
}

# ==================== SWAP CONFIGURATION ====================
setup_swap() {
    step "Настройка swap-файла"
    
    # Check existing swap
    local existing_swap=$(free -m | grep Swap | awk '{print $2}')
    if [[ $existing_swap -gt 0 ]]; then
        warn "Swap уже настроен: ${existing_swap}MB"
        read -p "Пересоздать swap? [y/N]: " recreate
        if [[ ! "$recreate" =~ ^[Yy]$ ]]; then
            return
        fi
        swapoff -a 2>/dev/null || true
    fi
    
    echo "Выберите размер swap:"
    echo "  1) 1GB (минимальный)"
    echo "  2) 2GB (рекомендуется для 1-2GB RAM)"
    echo "  3) 4GB (рекомендуется для 2-4GB RAM)"
    echo "  4) 8GB (для серверов с большой нагрузкой)"
    echo "  5) Свой размер"
    echo "  0) Пропустить"
    echo ""
    
    read -p "Выберите [0-5]: " swap_choice
    
    case $swap_choice in
        0) warn "Swap не настроен"; return ;;
        1) SWAP_SIZE="1G" ;;
        2) SWAP_SIZE="2G" ;;
        3) SWAP_SIZE="4G" ;;
        4) SWAP_SIZE="8G" ;;
        5)
            read -p "Введите размер (например, 3G): " SWAP_SIZE
            ;;
        *) SWAP_SIZE="2G" ;;
    esac
    
    local SWAP_FILE="/swapfile"
    
    info "Создание swap-файла размером $SWAP_SIZE..."
    fallocate -l "$SWAP_SIZE" "$SWAP_FILE" || dd if=/dev/zero of="$SWAP_FILE" bs=1M count="${SWAP_SIZE//G/}000"
    chmod 600 "$SWAP_FILE"
    mkswap "$SWAP_FILE"
    swapon "$SWAP_FILE"
    
    # Add to fstab if not present
    if ! grep -q "$SWAP_FILE" /etc/fstab; then
        echo "$SWAP_FILE none swap sw 0 0" >> /etc/fstab
    fi
    
    # Optimize swappiness
    sysctl vm.swappiness=10
    if ! grep -q "vm.swappiness" /etc/sysctl.conf; then
        echo "vm.swappiness=10" >> /etc/sysctl.conf
    fi
    
    save_state "swap_size" "$SWAP_SIZE"
    info "Swap настроен: $SWAP_SIZE"
}

# ==================== HOSTNAME ====================
setup_hostname() {
    step "Настройка hostname"
    
    local current_hostname=$(hostname)
    echo "Текущий hostname: $current_hostname"
    echo ""
    
    read -p "Установить новый hostname? [y/N]: " change_hn
    if [[ ! "$change_hn" =~ ^[Yy]$ ]]; then
        return
    fi
    
    read -p "Введите новый hostname: " new_hostname
    if [[ -z "$new_hostname" ]]; then
        warn "Hostname не изменён"
        return
    fi
    
    hostnamectl set-hostname "$new_hostname"
    
    # Update /etc/hosts
    sed -i "s/127.0.1.1.*/127.0.1.1\t$new_hostname/" /etc/hosts
    
    save_state "hostname" "$new_hostname"
    info "Hostname установлен: $new_hostname"
}

# ==================== FAIL2BAN WITH DYNAMIC BLACKLIST ====================
install_fail2ban() {
    step "Установка Fail2Ban с динамическим blacklist"
    
    apt-get install -y fail2ban
    
    local F2B_DIR="/etc/fail2ban"
    local BLACKLIST="$BASE/fail2ban/blacklist.conf"
    local WHITELIST="$BASE/fail2ban/whitelist.conf"
    
    mkdir -p "$BASE/fail2ban"
    touch "$BLACKLIST" "$WHITELIST"
    
    # Create custom jail
    cat > "$F2B_DIR/jail.local" <<'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
destemail = root@localhost
sendername = Fail2Ban
action = %(action_mwl)s

# Blacklist from file
banaction = iptables-multiport[blacklist=/srv/sys/fail2ban/blacklist.conf]

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
bantime = 7200

[sshd-aggressive]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 10
findtime = 3600
bantime = 86400
EOF

    # Dynamic blacklist update script
    cat > "$BASE/fail2ban/update_blacklist.sh" <<'SCRIPT'
#!/usr/bin/env bash
BLACKLIST="/srv/sys/fail2ban/blacklist.conf"
WHITELIST="/srv/sys/fail2ban/whitelist.conf"

# Add IP to blacklist
add_to_blacklist() {
    local ip="$1"
    if ! grep -q "^$ip$" "$WHITELIST" 2>/dev/null; then
        if ! grep -q "^$ip$" "$BLACKLIST" 2>/dev/null; then
            echo "$ip" >> "$BLACKLIST"
            fail2ban-client set sshd banip "$ip"
            echo "[$(date)] Added $ip to blacklist" >> /var/log/fail2ban-dynamic.log
        fi
    fi
}

# Remove IP from blacklist
remove_from_blacklist() {
    local ip="$1"
    sed -i "/^$ip$/d" "$BLACKLIST"
    fail2ban-client set sshd unbanip "$ip" 2>/dev/null || true
    echo "[$(date)] Removed $ip from blacklist" >> /var/log/fail2ban-dynamic.log
}

# Auto-ban IPs with multiple failed attempts
analyze_logs() {
    tail -1000 /var/log/auth.log | grep "Failed password" | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | while read count ip; do
        if [[ $count -ge 10 ]]; then
            add_to_blacklist "$ip"
        fi
    done
}

case "${1:-}" in
    add) add_to_blacklist "$2" ;;
    remove) remove_from_blacklist "$2" ;;
    analyze) analyze_logs ;;
    *) echo "Usage: $0 {add|remove|analyze} [IP]" ;;
esac
SCRIPT
    
    chmod +x "$BASE/fail2ban/update_blacklist.sh"
    
    # Systemd timer for auto-analysis
    cat > /etc/systemd/system/fail2ban-analyze.service <<EOF
[Unit]
Description=Fail2Ban Dynamic Blacklist Analysis
After=network.target

[Service]
Type=oneshot
ExecStart=$BASE/fail2ban/update_blacklist.sh analyze
EOF

    cat > /etc/systemd/system/fail2ban-analyze.timer <<EOF
[Unit]
Description=Run Fail2Ban analysis every 15 minutes

[Timer]
OnBootSec=5min
OnUnitActiveSec=15min
Persistent=true

[Install]
WantedBy=timers.target
EOF

    systemctl daemon-reload
    systemctl enable --now fail2ban
    systemctl enable --now fail2ban-analyze.timer
    
    save_state "fail2ban" "installed"
    info "Fail2Ban установлен с динамическим blacklist"
    info "Управление: $BASE/fail2ban/update_blacklist.sh {add|remove} <IP>"
}

# ==================== UNATTENDED UPGRADES ====================
install_unattended_upgrades() {
    step "Установка автоматических обновлений безопасности"
    
    apt-get install -y unattended-upgrades apt-listchanges
    
    cat > /etc/apt/apt.conf.d/50unattended-upgrades <<'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-New-Unused-Dependencies "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Automatic-Reboot-Time "03:00";
EOF

    cat > /etc/apt/apt.conf.d/20auto-upgrades <<EOF
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
EOF

    systemctl restart unattended-upgrades
    
    save_state "unattended_upgrades" "installed"
    info "Автоматические обновления безопасности активированы"
}

# ==================== DOCKER ====================
install_docker() {
    step "Установка Docker и Docker Compose"
    
    read -p "Установить Docker? [y/N]: " install_docker
    if [[ ! "$install_docker" =~ ^[Yy]$ ]]; then
        return
    fi
    
    info "Удаление старых версий Docker..."
    apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    info "Установка зависимостей..."
    apt-get install -y ca-certificates curl gnupg lsb-release
    
    info "Добавление GPG ключа Docker..."
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    info "Добавление репозитория Docker..."
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    apt-get update -qq
    
    info "Установка Docker Engine..."
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Enable Docker service
    systemctl enable --now docker
    
    # Add current user to docker group if not root
    if [[ -n "${SUDO_USER:-}" ]]; then
        usermod -aG docker "$SUDO_USER"
        info "Пользователь $SUDO_USER добавлен в группу docker"
    fi
    
    save_state "docker" "installed"
    info "Docker установлен: $(docker --version)"
    info "Docker Compose: $(docker compose version)"
}

# ==================== GIT ====================
setup_git() {
    step "Настройка Git"
    
    read -p "Настроить Git? [y/N]: " setup_git
    if [[ ! "$setup_git" =~ ^[Yy]$ ]]; then
        return
    fi
    
    apt-get install -y git
    
    read -p "Имя для Git commits: " git_name
    read -p "Email для Git commits: " git_email
    
    if [[ -n "$git_name" ]]; then
        git config --global user.name "$git_name"
    fi
    
    if [[ -n "$git_email" ]]; then
        git config --global user.email "$git_email"
    fi
    
    git config --global init.defaultBranch main
    git config --global pull.rebase false
    
    save_state "git_configured" "yes"
    info "Git настроен"
}

# ==================== PYTHON ====================
install_python() {
    step "Установка Python и окружения"
    
    read -p "Установить Python? [y/N]: " install_py
    if [[ ! "$install_py" =~ ^[Yy]$ ]]; then
        return
    fi
    
    echo "Выберите версию Python:"
    echo "  1) Python 3.10"
    echo "  2) Python 3.11"
    echo "  3) Python 3.12 (latest)"
    echo "  4) Все версии (через pyenv)"
    echo ""
    
    read -p "Выберите [1-4]: " py_choice
    
    info "Установка зависимостей для Python..."
    apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
        libreadline-dev libsqlite3-dev curl libffi-dev libncursesw5-dev \
        xz-utils tk-dev libxml2-dev libxmlsec1-dev liblzma-dev
    
    case $py_choice in
        4)
            info "Установка pyenv для управления версиями Python..."
            curl https://pyenv.run | bash
            export PYENV_ROOT="$HOME/.pyenv"
            export PATH="$PYENV_ROOT/bin:$PATH"
            eval "$(pyenv init --path)"
            eval "$(pyenv init -)"
            
            info "Установка Python 3.10, 3.11, 3.12..."
            pyenv install 3.10.13 && pyenv install 3.11.7 && pyenv install 3.12.1
            pyenv global 3.12.1
            PY_VER="3.12 (pyenv)"
            ;;
        1) 
            PY_VER="3.10"
            apt-get install -y python3.10 python3.10-venv python3.10-dev
            update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
            ;;
        2) 
            PY_VER="3.11"
            add-apt-repository -y ppa:deadsnakes/ppa && apt-get update
            apt-get install -y python3.11 python3.11-venv python3.11-dev
            update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
            ;;
        3|*) 
            PY_VER="3.12"
            add-apt-repository -y ppa:deadsnakes/ppa && apt-get update
            apt-get install -y python3.12 python3.12-venv python3.12-dev python3.12-distutils
            update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
            ;;
    esac
    
    info "Установка pip и менеджеров пакетов..."
    apt-get install -y python3-pip
    python3 -m pip install --upgrade pip setuptools wheel
    python3 -m pip install virtualenv pipenv poetry
    
    info "Установка популярных Python пакетов..."
    python3 -m pip install --upgrade \
        requests flask django fastapi uvicorn gunicorn \
        celery redis pymongo psycopg2-binary sqlalchemy \
        pytest black flake8 ipython jupyter numpy pandas 2>/dev/null || true
    
    read -p "Установить Jupyter Lab? [y/N]: " inst_jupyter
    if [[ "$inst_jupyter" =~ ^[Yy]$ ]]; then
        python3 -m pip install jupyterlab notebook
        mkdir -p ~/.jupyter
        cat > ~/.jupyter/jupyter_notebook_config.py <<'EOF'
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.port = 8888
c.NotebookApp.open_browser = False
c.NotebookApp.allow_remote_access = True
EOF
        info "Jupyter Lab установлен. Запуск: jupyter-lab"
        info "Доступ: http://$(hostname -I | awk '{print $1}'):8888"
    fi
    
    save_state "python_version" "$PY_VER"
    info "Python ${PY_VER} установлен: $(python3 --version)"
    info "pip: $(pip3 --version)"
}

# ==================== BASE PACKAGES ====================
install_base_packages() {
    step "Установка базовых пакетов"
    
    local packages=(
        "curl" "wget" "vim" "nano" "htop" "net-tools"
        "apt-transport-https" "ca-certificates" "software-properties-common"
        "iptables" "iptables-persistent" "ipset" "rsync" "zip" "unzip"
        "build-essential" "gcc" "make" "automake"
    )
    
    info "Установка: ${packages[*]}"
    apt-get install -y "${packages[@]}"
    
    save_state "base_packages" "installed"
    info "Базовые пакеты установлены"
}

# ==================== SERVICE DEPLOYMENT MASTER ====================

# Web Server with Progressive Login
deploy_web_server() {
    step "Развёртывание Web-сервера"
    
    read -p "Доменное имя (или IP): " DOMAIN
    read -p "Email для SSL сертификата: " SSL_EMAIL
    
    DOMAIN="${DOMAIN:-$(hostname -I | awk '{print $1}')}"
    SSL_EMAIL="${SSL_EMAIL:-admin@localhost}"
    
    info "Установка Nginx и всех необходимых модулей..."
    apt-get install -y nginx nginx-extras nginx-common \
        certbot python3-certbot-nginx \
        openssl ssl-cert \
        apache2-utils \
        geoip-database libgeoip1 \
        libnginx-mod-http-geoip \
        libnginx-mod-http-headers-more-filter \
        libnginx-mod-http-cache-purge \
        libnginx-mod-http-fancyindex
    
    # Optimize Nginx config
    info "Оптимизация конфигурации Nginx..."
    cat > /etc/nginx/nginx.conf <<'NGINXCONF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 2048;
    use epoll;
    multi_accept on;
}

http {
    # Basic Settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    client_max_body_size 100M;
    
    # MIME
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # SSL Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    # Gzip Settings
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/rss+xml font/truetype font/opentype application/vnd.ms-fontobject image/svg+xml;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;
    limit_conn_zone $binary_remote_addr zone=conn_limit:10m;
    
    # Virtual Host Configs
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
NGINXCONF
    
    local WEBROOT="/var/www/$DOMAIN/html"
    mkdir -p "$WEBROOT"
    
    # Progressive login page with countdown
    cat > "$WEBROOT/index.html" <<'HTML'
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Авторизация</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: rgba(255, 255, 255, 0.95);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 400px;
            width: 100%;
            text-align: center;
        }
        .logo {
            width: 80px;
            height: 80px;
            margin: 0 auto 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
            color: white;
        }
        h1 { color: #333; margin-bottom: 30px; font-size: 24px; }
        input {
            width: 100%;
            padding: 15px;
            margin: 10px 0;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 15px;
            margin-top: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover { transform: translateY(-2px); }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .error {
            background: #ff4444;
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            display: none;
        }
        .countdown {
            font-size: 48px;
            font-weight: bold;
            color: #667eea;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🔐</div>
        <h1>Вход в систему</h1>
        <form id="loginForm">
            <input type="text" id="username" placeholder="Логин" required>
            <input type="password" id="password" placeholder="Пароль" required>
            <button type="submit" id="submitBtn">Войти</button>
        </form>
        <div class="error" id="error">
            Неверные учётные данные!<br>
            Повторная попытка через: <div class="countdown" id="countdown"></div>
        </div>
    </div>

    <script>
        let attempts = 0;
        const delays = [5, 15, 30, 60, 120, 300, 600, 1800, 3600];
        
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const delay = delays[Math.min(attempts, delays.length - 1)];
            attempts++;
            
            document.getElementById('error').style.display = 'block';
            document.getElementById('submitBtn').disabled = true;
            
            let remaining = delay;
            document.getElementById('countdown').textContent = remaining;
            
            const interval = setInterval(() => {
                remaining--;
                document.getElementById('countdown').textContent = remaining;
                
                if (remaining <= 0) {
                    clearInterval(interval);
                    document.getElementById('error').style.display = 'none';
                    document.getElementById('submitBtn').disabled = false;
                    document.getElementById('loginForm').reset();
                }
            }, 1000);
        });
    </script>
</body>
</html>
HTML

    # Nginx config with rate limiting and security
    cat > "/etc/nginx/sites-available/$DOMAIN" <<EOF
# Rate limiting zones for progressive blocking
limit_req_zone \$binary_remote_addr zone=${DOMAIN}_login:10m rate=3r/m;
limit_req_zone \$binary_remote_addr zone=${DOMAIN}_global:10m rate=10r/s;

# Connection limiting
limit_conn_zone \$binary_remote_addr zone=${DOMAIN}_conn:10m;

# Geo-blocking (optional - uncomment to enable)
# geo \$block_country {
#     default 0;
#     include /etc/nginx/conf.d/blocked_countries.conf;
# }

server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;
    
    root $WEBROOT;
    index index.html;
    
    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Rate limiting - global
    limit_req zone=${DOMAIN}_global burst=20 nodelay;
    limit_conn ${DOMAIN}_conn 10;
    
    # Main location with progressive rate limiting
    location / {
        try_files \$uri \$uri/ =404;
    }
    
    # Login endpoint with strict rate limiting
    location ~ ^/(login|auth) {
        limit_req zone=${DOMAIN}_login burst=2 nodelay;
        try_files \$uri \$uri/ =404;
    }
    
    # Static assets caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # Logging with detailed info
    access_log /var/log/nginx/${DOMAIN}_access.log combined;
    error_log /var/log/nginx/${DOMAIN}_error.log warn;
    
    # Real IP detection (if behind proxy/CDN)
    # real_ip_header X-Forwarded-For;
    # set_real_ip_from 173.245.48.0/20; # Cloudflare IPs example
}
EOF

    ln -sf "/etc/nginx/sites-available/$DOMAIN" "/etc/nginx/sites-enabled/$DOMAIN"
    rm -f /etc/nginx/sites-enabled/default
    
    nginx -t && systemctl reload nginx
    
    # SSL Certificate
    if [[ "$DOMAIN" != *"."*"."* ]] && [[ "$DOMAIN" =~ ^[0-9]+\. ]]; then
        warn "Домен выглядит как IP, пропускаем SSL"
    else
        info "Получение SSL сертификата..."
        certbot --nginx -n --agree-tos --redirect -m "$SSL_EMAIL" -d "$DOMAIN" || warn "Не удалось получить SSL"
    fi
    
    # iptables - Nginx
    iptables -C INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 80 -j ACCEPT
    iptables -C INPUT -p tcp --dport 443 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 443 -j ACCEPT
    mkdir -p /etc/iptables && iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
    
    save_state "web_deployed" "yes"
    info "Web-сервер развёрнут: http://$DOMAIN"
}

# Mail Server
deploy_mail_server() {
    step "Развёртывание Mail-сервера"
    
    read -p "Доменное имя для почты: " MAIL_DOMAIN
    read -p "Выберите MTA (1=Postfix, 2=Exim4): " mta_choice
    
    info "Установка общих почтовых утилит..."
    apt-get install -y mailutils bsd-mailx libsasl2-modules libsasl2-modules-sql \
        libsasl2-2 sasl2-bin libdb5.3 libdb5.3-dev db-util \
        opendkim opendkim-tools postfix-policyd-spf-python \
        spamassassin spamc razor pyzor \
        amavisd-new clamav clamav-daemon \
        postgrey
    
    if [[ "$mta_choice" == "2" ]]; then
        info "Установка Exim4 с полным набором модулей..."
        apt-get install -y exim4 exim4-daemon-heavy exim4-config exim4-base \
            exim4-doc-html exim4-doc-info
        
        # Basic Exim4 configuration
    read -p "Установить Roundcube webmail? [y/N]: " install_roundcube
    if [[ "$install_roundcube" =~ ^[Yy]$ ]]; then
        info "Установка Roundcube с плагинами..."
        apt-get install -y roundcube roundcube-mysql roundcube-plugins \
            roundcube-plugins-extra php-net-smtp php-net-socket \
            php-mail-mime php-mail-mimedecode php-net-ldap3
        
        # Configure Roundcube
        info "Настройка Roundcube..."
        cat > /etc/roundcube/config.inc.php <<'RCCONF'
<?php
\$config['db_dsnw'] = 'mysql://roundcube:password@localhost/roundcube';
\$config['default_host'] = 'ssl://localhost';
\$config['default_port'] = 993;
\$config['smtp_server'] = 'tls://localhost';
\$config['smtp_port'] = 587;
\$config['smtp_user'] = '%u';
\$config['smtp_pass'] = '%p';
\$config['support_url'] = '';
\$config['product_name'] = 'Webmail';
\$config['des_key'] = '$(openssl rand -hex 24)';
# Database Server
deploy_database() {
    step "Развёртывание Database-сервера"
    
    echo "Выберите СУБД:"
    echo "  1) MySQL 8.0"
    echo "  2) PostgreSQL 15"
    echo "  3) MariaDB 10.11"
    echo "  4) MongoDB 7.0"
    echo "  5) Redis (кэш)"
    echo ""
    
    read -p "Выбор [1-5]: " db_choice
    
    case $db_choice in
        1)
            info "Установка MySQL 8.0 с полным набором инструментов..."
            apt-get install -y mysql-server mysql-client \
                mysql-common libmysqlclient-dev \
                mytop innotop percona-toolkit \
                mysql-utilities mycli
            
            info "Оптимизация MySQL..."
            cat > /etc/mysql/mysql.conf.d/optimization.cnf <<'MYSQLOPT'
[mysqld]
# Performance
max_connections = 200
thread_cache_size = 16
query_cache_type = 1
query_cache_size = 64M
query_cache_limit = 2M
tmp_table_size = 64M
max_heap_table_size = 64M
table_open_cache = 4000
open_files_limit = 8000

# InnoDB
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT
innodb_file_per_table = 1
# VPN Server
deploy_vpn() {
    step "Развёртывание VPN-сервера"
    
    echo "Выберите VPN:"
    echo "  1) OpenVPN (полная установка)"
    echo "  2) WireGuard (современный, быстрый)"
    echo "  3) IKEv2/IPsec (strongSwan)"
    echo "  4) L2TP/IPsec"
    echo ""
    
    read -p "Выбор [1-4]: " vpn_choice
    
    case $vpn_choice in
        2)
            info "Установка WireGuard с полным набором утилит..."
            apt-get install -y wireguard wireguard-tools qrencode resolvconf
            
            # Enable IP forwarding
            echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
            echo "net.ipv6.conf.all.forwarding=1" >> /etc/sysctl.conf
            sysctl -p
            
            mkdir -p /etc/wireguard
            cd /etc/wireguard
            
            # Generate server keys
            wg genkey | tee server_private.key | wg pubkey > server_public.key
            chmod 600 server_private.key
            
            local SERVER_IP=$(hostname -I | awk '{print $1}')
            local SERVER_PUB_KEY=$(cat server_public.key)
            local SERVER_PRIV_KEY=$(cat server_private.key)
            
            # Main interface detection
            local MAIN_IF=$(ip route | grep default | awk '{print $5}' | head -1)
            
            cat > /etc/wireguard/wg0.conf <<EOF
[Interface]
PrivateKey = $SERVER_PRIV_KEY
Address = 10.8.0.1/24, fd42:42:42::1/64
ListenPort = 51820
SaveConfig = false

# Forwarding
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o $MAIN_IF -j MASQUERADE; ip6tables -A FORWARD -i wg0 -j ACCEPT; ip6tables -t nat -A POSTROUTING -o $MAIN_IF -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o $MAIN_IF -j MASQUERADE; ip6tables -D FORWARD -i wg0 -j ACCEPT; ip6tables -t nat -D POSTROUTING -o $MAIN_IF -j MASQUERADE

# DNS
#PostUp = echo nameserver 1.1.1.1 | resolvconf -a wg0 -m 0 -x
#PostDown = resolvconf -d wg0
EOF
            
            # Generate client configs
            info "Генерация клиентских конфигов..."
            for i in {1..5}; do
                wg genkey | tee client${i}_private.key | wg pubkey > client${i}_public.key
                
                cat >> /etc/wireguard/wg0.conf <<EOF

[Peer]
# Client $i
PublicKey = $(cat client${i}_public.key)
AllowedIPs = 10.8.0.$((i+1))/32, fd42:42:42::$((i+1))/128
EOF

                cat > client${i}.conf <<EOF
[Interface]
PrivateKey = $(cat client${i}_private.key)
Address = 10.8.0.$((i+1))/24, fd42:42:42::$((i+1))/64
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = $SERVER_PUB_KEY
Endpoint = $SERVER_IP:51820
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
EOF
                
                # Generate QR code for mobile
                qrencode -t ansiutf8 < client${i}.conf
                qrencode -t png -o client${i}.png < client${i}.conf
            done
            
            chmod 600 /etc/wireguard/*.conf
            chmod 600 /etc/wireguard/*.key
            
            systemctl enable wg-quick@wg0
            systemctl start wg-quick@wg0
            
            # iptables rules
            iptables -C INPUT -p udp --dport 51820 -j ACCEPT 2>/dev/null || iptables -I INPUT -p udp --dport 51820 -j ACCEPT
            iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
            
            info "WireGuard установлен!"
            info "Server Public Key: $SERVER_PUB_KEY"
            info "Клиентские конфиги: /etc/wireguard/client*.conf"
            info "QR коды: /etc/wireguard/client*.png"
            ;;
            
        3)
            info "Установка IKEv2/IPsec (strongSwan)..."
            apt-get install -y strongswan strongswan-pki \
                libcharon-extra-plugins libcharon-extauth-plugins \
                libstrongswan-extra-plugins
            
            # Generate certificates
            mkdir -p /etc/ipsec.d/{cacerts,certs,private}
            cd /etc/ipsec.d
            
            ipsec pki --gen --type rsa --size 4096 --outform pem > private/ca-key.pem
            ipsec pki --self --ca --lifetime 3650 --in private/ca-key.pem \
                --type rsa --dn "CN=VPN CA" --outform pem > cacerts/ca-cert.pem
            
            ipsec pki --gen --type rsa --size 4096 --outform pem > private/server-key.pem
            ipsec pki --pub --in private/server-key.pem --type rsa | \
                ipsec pki --issue --lifetime 1825 \
                --cacert cacerts/ca-cert.pem --cakey private/ca-key.pem \
                --dn "CN=$(hostname)" --san "$(hostname -I | awk '{print $1}')" \
                --flag serverAuth --flag ikeIntermediate --outform pem > certs/server-cert.pem
            
            cat > /etc/ipsec.conf <<'IPSECCONF'
config setup
    charondebug="ike 1, knl 1, cfg 0"
    uniqueids=no

conn ikev2-vpn
    auto=add
    compress=no
    type=tunnel
    keyexchange=ikev2
    fragmentation=yes
    forceencaps=yes
    dpdaction=clear
    dpddelay=300s
    rekey=no
    left=%any
    leftid=$(hostname -I | awk '{print $1}')
    leftcert=server-cert.pem
    leftsendcert=always
    leftsubnet=0.0.0.0/0
    right=%any
    rightid=%any
    rightauth=eap-mschapv2
    rightsourceip=10.10.10.0/24
    rightdns=8.8.8.8,1.1.1.1
    rightsendcert=never
    eap_identity=%identity
IPSECCONF

            cat > /etc/ipsec.secrets <<EOF
: RSA "server-key.pem"
EOF

            systemctl restart strongswan-starter
            iptables -C INPUT -p udp --dport 500 -j ACCEPT 2>/dev/null || iptables -I INPUT -p udp --dport 500 -j ACCEPT
            iptables -C INPUT -p udp --dport 4500 -j ACCEPT 2>/dev/null || iptables -I INPUT -p udp --dport 4500 -j ACCEPT
            iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
            
            info "IKEv2/IPsec установлен!"
            info "CA сертификат: /etc/ipsec.d/cacerts/ca-cert.pem"
            ;;
            
        4)
            info "Установка L2TP/IPsec..."
            apt-get install -y xl2tpd strongswan strongswan-pki
            
            # Configure strongSwan
            cat > /etc/ipsec.conf <<'L2TPCONF'
config setup

conn %default
    ikelifetime=60m
    keylife=20m
    rekeymargin=3m
    keyingtries=1
    keyexchange=ikev1
    authby=secret
    ike=aes128-sha1-modp1024,3des-sha1-modp1024!
    esp=aes128-sha1-modp1024,3des-sha1-modp1024!

conn L2TP-PSK
    type=transport
    leftprotoport=17/1701
    rightprotoport=17/%any
    auto=add
L2TPCONF

            read -sp "PSK для L2TP (pre-shared key): " L2TP_PSK
            echo ""
            cat > /etc/ipsec.secrets <<EOF
: PSK "$L2TP_PSK"
EOF

            # Configure xl2tpd
            cat > /etc/xl2tpd/xl2tpd.conf <<'XL2TPDCONF'
[global]
port = 1701

[lns default]
ip range = 10.20.0.2-10.20.0.254
local ip = 10.20.0.1
require chap = yes
refuse pap = yes
require authentication = yes
name = l2tpd
ppp debug = yes
pppoptfile = /etc/ppp/options.xl2tpd
length bit = yes
XL2TPDCONF

            cat > /etc/ppp/options.xl2tpd <<'PPPOPT'
ipcp-accept-local
ipcp-accept-remote
ms-dns 8.8.8.8
ms-dns 1.1.1.1
noccp
auth
crtscts
idle 1800
mtu 1280
mru 1280
nodefaultroute
debug
lock
proxyarp
connect-delay 5000
PPPOPT

            read -p "VPN username: " vpn_user
            read -sp "VPN password: " vpn_pass
            echo ""
            echo "$vpn_user l2tpd $vpn_pass *" >> /etc/ppp/chap-secrets
            
            systemctl restart strongswan-starter xl2tpd
            iptables -C INPUT -p udp --dport 1701 -j ACCEPT 2>/dev/null || iptables -I INPUT -p udp --dport 1701 -j ACCEPT
            iptables -C INPUT -p udp --dport 500 -j ACCEPT 2>/dev/null || iptables -I INPUT -p udp --dport 500 -j ACCEPT
            iptables -C INPUT -p udp --dport 4500 -j ACCEPT 2>/dev/null || iptables -I INPUT -p udp --dport 4500 -j ACCEPT
            iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
            
            info "L2TP/IPsec установлен!"
            ;;
            
        1|*)
            info "Установка OpenVPN с Easy-RSA..."
            apt-get install -y openvpn easy-rsa
            
            # Setup Easy-RSA
            make-cadir /etc/openvpn/easy-rsa
            cd /etc/openvpn/easy-rsa
            
            ./easyrsa init-pki
            echo "VPN-CA" | ./easyrsa build-ca nopass
            ./easyrsa gen-dh
            ./easyrsa build-server-full server nopass
            
            # Generate clients
            for i in {1..5}; do
                ./easyrsa build-client-full client$i nopass
            done
            
            openvpn --genkey secret /etc/openvpn/ta.key
            
            # Server config
            cat > /etc/openvpn/server.conf <<'OVPNCONF'
port 1194
proto udp
dev tun
ca /etc/openvpn/easy-rsa/pki/ca.crt
cert /etc/openvpn/easy-rsa/pki/issued/server.crt
key /etc/openvpn/easy-rsa/pki/private/server.key
dh /etc/openvpn/easy-rsa/pki/dh.pem
tls-auth /etc/openvpn/ta.key 0
server 10.9.0.0 255.255.255.0
ifconfig-pool-persist /var/log/openvpn/ipp.txt
push "redirect-gateway def1 bypass-dhcp"
push "dhcp-option DNS 8.8.8.8"
push "dhcp-option DNS 1.1.1.1"
keepalive 10 120
cipher AES-256-CBC
auth SHA256
user nobody
group nogroup
persist-key
persist-tun
status /var/log/openvpn/openvpn-status.log
log-append /var/log/openvpn/openvpn.log
verb 3
explicit-exit-notify 1
OVPNCONF

            mkdir -p /var/log/openvpn
            systemctl enable --now openvpn@server
            
            # Generate client configs
            mkdir -p /etc/openvpn/clients
            local SERVER_IP=$(hostname -I | awk '{print $1}')
            
            for i in {1..5}; do
                cat > /etc/openvpn/clients/client$i.ovpn <<EOF
client
dev tun
proto udp
remote $SERVER_IP 1194
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-CBC
auth SHA256
verb 3

<ca>
$(cat /etc/openvpn/easy-rsa/pki/ca.crt)
</ca>

<cert>
$(cat /etc/openvpn/easy-rsa/pki/issued/client$i.crt)
</cert>

<key>
$(cat /etc/openvpn/easy-rsa/pki/private/client$i.key)
</key>

<tls-auth>
$(cat /etc/openvpn/ta.key)
</tls-auth>
key-direction 1
EOF
            done
            
            # MikroTik config
            read -p "Создать конфиг для MikroTik? [y/N]: " mikrotik_conf
            if [[ "$mikrotik_conf" =~ ^[Yy]$ ]]; then
                info "Создание конфига для MikroTik RouterOS..."
                cat > /etc/openvpn/clients/mikrotik.rsc <<EOF
# MikroTik RouterOS OpenVPN Client Configuration
# Import certificates first:
# /certificate import file-name=ca.crt
# /certificate import file-name=client.crt
# /certificate import file-name=client.key

/interface ovpn-client
add certificate=client.crt_0 \\
    cipher=aes256 \\
    connect-to=$SERVER_IP \\
    mac-address=FE:xx:xx:xx:xx:xx \\
    name=ovpn-out1 \\
    port=1194 \\
    user=client1

/ip firewall nat
add action=masquerade chain=srcnat out-interface=ovpn-out1
EOF
                info "MikroTik конфиг создан: /etc/openvpn/clients/mikrotik.rsc"
            fi
            
            iptables -C INPUT -p udp --dport 1194 -j ACCEPT 2>/dev/null || iptables -I INPUT -p udp --dport 1194 -j ACCEPT
            iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
            
            info "OpenVPN установлен!"
            info "Клиентские конфиги: /etc/openvpn/clients/"
            ;;
    esac
    
    # Enable IP forwarding
    echo 1 > /proc/sys/net/ipv4/ip_forward
    echo 1 > /proc/sys/net/ipv6/conf/all/forwarding
    
    save_state "vpn_deployed" "yes"
    save_state "vpn_type" "$vpn_choice"
    info "VPN сервер полностью настроен и запущен"
}in_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 4
max_parallel_workers_per_gather = 2
max_parallel_workers = 4
max_parallel_maintenance_workers = 2

# Connection Settings
max_connections = 200
PGOPT

            systemctl restart postgresql
            
            info "Создание административного пользователя..."
            read -p "Имя админа БД: " db_admin
            read -sp "Пароль админа БД: " db_pass
            echo ""
            sudo -u postgres psql -c "CREATE USER $db_admin WITH PASSWORD '$db_pass' SUPERUSER CREATEDB CREATEROLE;"
            ;;
            
        3)
            info "Установка MariaDB 10.11 с дополнениями..."
            apt-get install -y mariadb-server mariadb-client \
                mariadb-common libmariadb-dev \
                mariadb-backup mytop \
                mysql-utilities mycli
            
            info "Оптимизация MariaDB..."
            cat > /etc/mysql/mariadb.conf.d/90-optimization.cnf <<'MARIAOPT'
[mysqld]
# Performance
max_connections = 200
thread_cache_size = 16
table_open_cache = 4000
query_cache_type = 1
query_cache_size = 64M

# InnoDB
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2
innodb_file_per_table = 1

# Aria Storage Engine
aria_pagecache_buffer_size = 128M

# Logging
slow_query_log = 1
slow_query_log_file = /var/log/mysql/mariadb-slow.log
long_query_time = 2
MARIAOPT

            systemctl restart mariadb
            mysql_secure_installation
            ;;
            
        4)
            info "Установка MongoDB 7.0..."
            curl -fsSL https://pgp.mongodb.com/server-7.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg
            echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
            apt-get update
            apt-get install -y mongodb-org mongodb-org-tools mongodb-mongosh
            
            info "Оптимизация MongoDB..."
            cat > /etc/mongod.conf <<'MONGOCONF'
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true
  engine: wiredTiger
  wiredTiger:
    engineConfig:
      cacheSizeGB: 1

systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log

net:
  port: 27017
  bindIp: 127.0.0.1

processManagement:
  timeZoneInfo: /usr/share/zoneinfo

security:
  authorization: enabled
MONGOCONF

            systemctl enable --now mongod
            
            info "Создание административного пользователя MongoDB..."
            read -p "Имя админа БД: " db_admin
            read -sp "Пароль админа БД: " db_pass
            echo ""
            mongosh <<EOF
use admin
db.createUser({
  user: "$db_admin",
  pwd: "$db_pass",
  roles: [ { role: "userAdminAnyDatabase", db: "admin" }, "readWriteAnyDatabase" ]
})
EOF
            systemctl restart mongod
            ;;
            
        5)
            info "Установка Redis с модулями..."
            apt-get install -y redis-server redis-tools \
                redis-sentinel redis-redisearch redis-redisgraph
            
            info "Оптимизация Redis..."
            cat > /etc/redis/redis.conf <<'REDISCONF'
bind 127.0.0.1 ::1
protected-mode yes
port 6379
tcp-backlog 511
timeout 0
tcp-keepalive 300
daemonize yes
supervised systemd
pidfile /var/run/redis/redis-server.pid
loglevel notice
logfile /var/log/redis/redis-server.log
databases 16

# Snapshotting
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /var/lib/redis

# Replication
replica-serve-stale-data yes
replica-read-only yes

# Security
requirepass $(openssl rand -base64 32)

# Memory Management
maxmemory 512mb
maxmemory-policy allkeys-lru

# AOF
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
REDISCONF

            systemctl restart redis-server
            info "Redis password: $(grep requirepass /etc/redis/redis.conf | awk '{print $2}')"
            ;;
    esac
    
    # Install common DB tools
    info "Установка общих инструментов БД..."
    apt-get install -y phpmyadmin adminer dbeaver-ce 2>/dev/null || true
    
    save_state "database_deployed" "yes"
    save_state "database_type" "$db_choice"
    info "Database установлена и оптимизирована"
}   chown opendkim:opendkim default.private
    
    cat > /etc/opendkim.conf <<EOF
Syslog yes
UMask 002
Socket inet:8891@localhost
KeyTable /etc/opendkim/KeyTable
SigningTable refile:/etc/opendkim/SigningTable
ExternalIgnoreList refile:/etc/opendkim/TrustedHosts
InternalHosts refile:/etc/opendkim/TrustedHosts
EOF

    echo "default._domainkey.$MAIL_DOMAIN $MAIL_DOMAIN:default:/etc/opendkim/keys/$MAIL_DOMAIN/default.private" > /etc/opendkim/KeyTable
    echo "*@$MAIL_DOMAIN default._domainkey.$MAIL_DOMAIN" > /etc/opendkim/SigningTable
    echo "127.0.0.1" > /etc/opendkim/TrustedHosts
    echo "localhost" >> /etc/opendkim/TrustedHosts
    echo "$MAIL_DOMAIN" >> /etc/opendkim/TrustedHosts
    
    systemctl restart opendkim
    
    info "DKIM public key (добавьте в DNS):"
    cat /etc/opendkim/keys/$MAIL_DOMAIN/default.txtrthost=''
CCONFDIR='/etc/exim4'
dc_use_split_config='false'
dc_hide_mailname='true'
dc_mailname_in_oh='true'
dc_localdelivery='maildir_home'
EOF
        update-exim4.conf
        systemctl restart exim4
    else
        info "Установка Postfix с полным набором модулей..."
        debconf-set-selections <<< "postfix postfix/mailname string $MAIL_DOMAIN"
        debconf-set-selections <<< "postfix postfix/main_mailer_type string 'Internet Site'"
        apt-get install -y postfix postfix-mysql postfix-pcre postfix-policyd-spf-python
        
        # Postfix optimization
        info "Оптимизация Postfix..."
        postconf -e "smtpd_banner = \$myhostname ESMTP"
        postconf -e "biff = no"
        postconf -e "append_dot_mydomain = no"
        postconf -e "readme_directory = no"
        postconf -e "compatibility_level = 2"
        postconf -e "smtpd_tls_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem"
        postconf -e "smtpd_tls_key_file=/etc/ssl/private/ssl-cert-snakeoil.key"
        postconf -e "smtpd_tls_security_level=may"
        postconf -e "smtp_tls_CApath=/etc/ssl/certs"
        postconf -e "smtp_tls_security_level=may"
        postconf -e "smtp_tls_session_cache_database = btree:\${data_directory}/smtp_scache"
        postconf -e "smtpd_relay_restrictions = permit_mynetworks permit_sasl_authenticated defer_unauth_destination"
        postconf -e "myhostname = $MAIL_DOMAIN"
        postconf -e "alias_maps = hash:/etc/aliases"
        postconf -e "alias_database = hash:/etc/aliases"
        postconf -e "myorigin = /etc/mailname"
        postconf -e "mydestination = \$myhostname, $MAIL_DOMAIN, localhost, localhost.localdomain"
        postconf -e "relayhost ="
        postconf -e "mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128"
        postconf -e "mailbox_size_limit = 0"
        postconf -e "recipient_delimiter = +"
        postconf -e "inet_interfaces = all"
        postconf -e "inet_protocols = all"
        
        # DKIM setup
        postconf -e "milter_default_action = accept"
        postconf -e "milter_protocol = 6"
        postconf -e "smtpd_milters = inet:localhost:8891"
        postconf -e "non_smtpd_milters = inet:localhost:8891"
        
        systemctl restart postfix
    fi
    
    info "Установка Dovecot с полным набором модулей..."
    apt-get install -y dovecot-core dovecot-imapd dovecot-pop3d \
        dovecot-lmtpd dovecot-mysql dovecot-pgsql dovecot-sqlite \
        dovecot-sieve dovecot-managesieved dovecot-solr \
        dovecot-submissiond dovecot-antispam
    
    # Dovecot configuration
    info "Настройка Dovecot..."
    cat > /etc/dovecot/conf.d/10-mail.conf <<'DOVECOTMAIL'
mail_location = maildir:~/Maildir
namespace inbox {
  inbox = yes
}
mail_privileged_group = mail
protocol !indexer-worker {
}
DOVECOTMAIL

    cat > /etc/dovecot/conf.d/10-auth.conf <<'DOVECOTAUTH'
disable_plaintext_auth = yes
auth_mechanisms = plain login
!include auth-system.conf.ext
DOVECOTAUTH

    cat > /etc/dovecot/conf.d/10-ssl.conf <<'DOVECOTSSL'
ssl = required
ssl_cert = </etc/ssl/certs/ssl-cert-snakeoil.pem
ssl_key = </etc/ssl/private/ssl-cert-snakeoil.key
ssl_min_protocol = TLSv1.2
ssl_cipher_list = ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384
ssl_prefer_server_ciphers = yes
DOVECOTSSL

    systemctl restart dovecot
    
    read -p "Установить Roundcube webmail? [y/N]: " install_roundcube
    if [[ "$install_roundcube" =~ ^[Yy]$ ]]; then
        apt-get install -y roundcube roundcube-mysql
    fi
    
    read -p "Настроить SSL для почты? [y/N]: " mail_ssl
    if [[ "$mail_ssl" =~ ^[Yy]$ ]]; then
        apt-get install -y certbot
        certbot certonly --standalone -d "$MAIL_DOMAIN" || warn "SSL не получен"
    fi
    
    # iptables - Mail ports
    iptables -C INPUT -p tcp --dport 25 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 25 -j ACCEPT
    iptables -C INPUT -p tcp --dport 587 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 587 -j ACCEPT
    iptables -C INPUT -p tcp --dport 143 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 143 -j ACCEPT
    iptables -C INPUT -p tcp --dport 993 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 993 -j ACCEPT
    iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
    
    save_state "mail_deployed" "yes"
    info "Mail-сервер развёрнут"
}

# Database Server
deploy_database() {
    step "Развёртывание Database-сервера"
    
    echo "Выберите СУБД:"
    echo "  1) MySQL"
    echo "  2) PostgreSQL"
    echo "  3) MariaDB"
    echo "  4) MongoDB"
    echo ""
    
    read -p "Выбор [1-4]: " db_choice
    
    case $db_choice in
        1)
            info "Установка MySQL..."
            apt-get install -y mysql-server
            mysql_secure_installation
            ;;
        2)
            info "Установка PostgreSQL..."
            apt-get install -y postgresql postgresql-contrib
            ;;
        3)
            info "Установка MariaDB..."
            apt-get install -y mariadb-server
            mysql_secure_installation
            ;;
        4)
            info "Установка MongoDB..."
            wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add -
            echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list
            apt-get update
            apt-get install -y mongodb-org
            systemctl enable --now mongod
            ;;
    esac
    
    save_state "database_deployed" "yes"
    info "Database установлена"
}

# VPN Server
deploy_vpn() {
    step "Развёртывание VPN-сервера"
    
    echo "Выберите VPN:"
    echo "  1) OpenVPN"
    echo "  2) WireGuard"
    echo ""
    
    read -p "Выбор [1-2]: " vpn_choice
    
    if [[ "$vpn_choice" == "2" ]]; then
        info "Установка WireGuard..."
        apt-get install -y wireguard wireguard-tools
        
        cd /etc/wireguard
        wg genkey | tee server_private.key | wg pubkey > server_public.key
        chmod 600 server_private.key
        
        cat > /etc/wireguard/wg0.conf <<EOF
[Interface]
PrivateKey = $(cat server_private.key)
Address = 10.0.0.1/24
ListenPort = 51820
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
EOF
        
        systemctl enable wg-quick@wg0
        systemctl start wg-quick@wg0
        
        info "WireGuard установлен. Public key: $(cat server_public.key)"
    else
        info "Установка OpenVPN..."
        wget https://git.io/vpn -O openvpn-install.sh
        chmod +x openvpn-install.sh
        bash openvpn-install.sh
        
        read -p "Создать конфиг для MikroTik? [y/N]: " mikrotik_conf
        if [[ "$mikrotik_conf" =~ ^[Yy]$ ]]; then
            info "Конвертация в формат MikroTik..."
            # MikroTik specific config would go here
            warn "Конфигурация для MikroTik требует ручной настройки"
        fi
    fi
    
    save_state "vpn_deployed" "yes"
    info "VPN сервер развёрнут"
}

# FTP Server
deploy_ftp() {
    step "Развёртывание FTP-сервера"
    
    echo "Выберите FTP сервер:"
    echo "  1) vsftpd (Very Secure FTP)"
    echo "  2) ProFTPD (с модулями)"
    echo "  3) Pure-FTPd"
    read -p "Выбор [1-3]: " ftp_choice
    
    case $ftp_choice in
        2)
            apt-get install -y proftpd proftpd-mod-mysql
            openssl req -new -x509 -days 365 -nodes -out /etc/ssl/certs/proftpd.crt -keyout /etc/ssl/private/proftpd.key -subj "/C=US/ST=State/CN=$(hostname)"
            ;;
        3)
            apt-get install -y pure-ftpd pure-ftpd-mysql
            echo "yes" > /etc/pure-ftpd/conf/ChrootEveryone
            echo "40000 40100" > /etc/pure-ftpd/conf/PassivePortRange
            systemctl restart pure-ftpd
            ;;
        *)
            apt-get install -y vsftpd libpam-pwdfile apache2-utils
            openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/vsftpd.key -out /etc/ssl/certs/vsftpd.crt -subj "/CN=$(hostname)"
            
            cat > /etc/vsftpd.conf <<'EOF'
listen=YES
anonymous_enable=NO
local_enable=YES
write_enable=YES
chroot_local_user=YES
rsa_cert_file=/etc/ssl/certs/vsftpd.crt
rsa_private_key_file=/etc/ssl/private/vsftpd.key
ssl_enable=YES
force_local_data_ssl=YES
force_local_logins_ssl=YES
ssl_tlsv1=YES
ssl_sslv2=NO
ssl_sslv3=NO
pasv_enable=YES
pasv_min_port=40000
pasv_max_port=40100
max_clients=50
EOF
            systemctl restart vsftpd
            ;;
    esac
    
    iptables -C INPUT -p tcp --dport 21 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 21 -j ACCEPT
    iptables -C INPUT -p tcp --dport 40000:40100 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 40000:40100 -j ACCEPT
    iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
    save_state "ftp_deployed" "yes"
    info "FTP сервер развёрнут с SSL"
}

# DNS Server
deploy_dns() {
    step "Развёртывание DNS-сервера"
    
    echo "Выберите DNS сервер:"
    echo "  1) BIND9 (полнофункциональный)"
    echo "  2) Unbound (рекурсивный)"
    echo "  3) dnsmasq (легкий)"
    read -p "Выбор [1-3]: " dns_choice
    
    case $dns_choice in
        2)
            apt-get install -y unbound unbound-anchor
            cat > /etc/unbound/unbound.conf.d/server.conf <<'EOF'
server:
    interface: 0.0.0.0
    access-control: 0.0.0.0/0 allow
    hide-identity: yes
    hide-version: yes
forward-zone:
    name: "."
    forward-addr: 1.1.1.1
    forward-addr: 8.8.8.8
EOF
            systemctl restart unbound
            ;;
        3)
            apt-get install -y dnsmasq
            cat > /etc/dnsmasq.conf <<'EOF'
server=1.1.1.1
server=8.8.8.8
cache-size=10000
EOF
            systemctl restart dnsmasq
            ;;
        *)
            apt-get install -y bind9 bind9utils bind9-doc dnsutils
            cat > /etc/bind/named.conf.options <<'EOF'
options {
    directory "/var/cache/bind";
    forwarders { 1.1.1.1; 8.8.8.8; };
    dnssec-validation auto;
    listen-on { any; };
    allow-query { any; };
};
EOF
            systemctl restart bind9
            ;;
    esac
    
    iptables -C INPUT -p udp --dport 53 -j ACCEPT 2>/dev/null || iptables -I INPUT -p udp --dport 53 -j ACCEPT
    iptables -C INPUT -p tcp --dport 53 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 53 -j ACCEPT
    iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
    save_state "dns_deployed" "yes"
    info "DNS сервер установлен"
}

# Monitoring
deploy_monitoring() {
    step "Развёртывание системы мониторинга"
    
    echo "Выберите решение:"
    echo "  1) Netdata (real-time)"
    echo "  2) Prometheus + Grafana"
    echo "  3) Zabbix"
    echo "  4) Все утилиты"
    read -p "Выбор [1-4]: " mon_choice
    
    apt-get install -y htop iotop nethogs iftop sysstat vnstat glances
    
    case $mon_choice in
        2)
            info "Установка Prometheus + Grafana..."
            apt-get install -y prometheus grafana
            cat > /etc/prometheus/prometheus.yml <<'EOF'
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9090']
EOF
            systemctl enable --now prometheus grafana-server
            iptables -C INPUT -p tcp --dport 3000 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 3000 -j ACCEPT
            iptables -C INPUT -p tcp --dport 9090 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 9090 -j ACCEPT
            iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
            info "Grafana: http://$(hostname -I | awk '{print $1}'):3000 (admin/admin)"
            ;;
        3)
            info "Установка Zabbix..."
            wget https://repo.zabbix.com/zabbix/6.4/ubuntu/pool/main/z/zabbix-release/zabbix-release_6.4-1+ubuntu$(lsb_release -rs)_all.deb 2>/dev/null || true
            dpkg -i zabbix-release_*.deb 2>/dev/null || true
            apt-get update
            apt-get install -y zabbix-server-mysql zabbix-frontend-php zabbix-agent 2>/dev/null || true
            info "Настройте Zabbix через веб-интерфейс"
            ;;
        4)
            bash <(curl -Ss https://my-netdata.io/kickstart.sh) --dont-wait
            apt-get install -y prometheus grafana 2>/dev/null || true
            systemctl enable --now netdata prometheus grafana-server 2>/dev/null || true
            iptables -C INPUT -p tcp --dport 19999 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 19999 -j ACCEPT
            iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
            info "Все системы мониторинга установлены"
            ;;
        *)
            bash <(curl -Ss https://my-netdata.io/kickstart.sh) --dont-wait
            iptables -C INPUT -p tcp --dport 19999 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 19999 -j ACCEPT
            iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
            info "Netdata: http://$(hostname -I | awk '{print $1}'):19999"
            ;;
    esac
    
    save_state "monitoring_deployed" "yes"
    info "Мониторинг установлен и запущен"
}

# ==================== SERVICE REMOVAL ====================
remove_service() {
    step "Удаление сервиса"
    
    echo "Какой сервис удалить?"
    echo "  1) Web Server (Nginx)"
    echo "  2) Mail Server"
    echo "  3) Database"
    echo "  4) VPN"
    echo "  5) FTP"
    echo "  6) DNS"
    echo "  7) Monitoring"
    echo "  0) Назад"
    echo ""
    
    read -p "Выбор [0-7]: " remove_choice
    
    case $remove_choice in
        1)
            apt-get remove --purge -y nginx nginx-common certbot python3-certbot-nginx
            rm -rf /etc/nginx /var/www
            save_state "web_deployed" "no"
            ;;
        2)
            apt-get remove --purge -y postfix exim4 dovecot-core roundcube
            save_state "mail_deployed" "no"
            ;;
        3)
            apt-get remove --purge -y mysql-server postgresql mariadb-server mongodb-org
            save_state "database_deployed" "no"
            ;;
        4)
            apt-get remove --purge -y openvpn wireguard
            rm -rf /etc/openvpn /etc/wireguard
            save_state "vpn_deployed" "no"
            ;;
        5)
            apt-get remove --purge -y vsftpd
            save_state "ftp_deployed" "no"
            ;;
        6)
            apt-get remove --purge -y bind9
            save_state "dns_deployed" "no"
            ;;
        7)
            apt-get remove --purge -y netdata
            save_state "monitoring_deployed" "no"
            ;;
        0) return ;;
    esac
    
    apt-get autoremove -y
    info "Сервис удалён"
}

# ==================== MAIN MENU ====================
main_menu() {
    while true; do
        clear
        banner
        
        echo "╔════════════════════════════════════════════════════════════════╗"
        echo "║                      ГЛАВНОЕ МЕНЮ                              ║"
        echo "╚════════════════════════════════════════════════════════════════╝"
        echo ""
        echo " [БАЗОВАЯ НАСТРОЙКА]"
        echo "  1) Обновление системы и ядра"
        echo "  2) Настройка timezone и локали"
        echo "  3) Настройка swap-файла"
        echo "  4) Настройка hostname"
        echo "  5) Установка базовых пакетов"
        echo ""
        echo " [БЕЗОПАСНОСТЬ]"
        echo "  6) Установка Fail2Ban (с blacklist)"
        echo "  7) Автоматические обновления безопасности"
        echo ""
        echo " [ИНСТРУМЕНТЫ РАЗРАБОТКИ]"
        echo "  8) Установка Docker"
        echo "  9) Настройка Git"
        echo " 10) Установка Python"
        echo ""
        echo " [РАЗВЁРТЫВАНИЕ СЕРВИСОВ]"
        echo " 11) Web Server (Nginx + прогрессивная авторизация)"
        echo " 12) Mail Server (Postfix/Exim + Dovecot + Roundcube)"
        echo " 13) Database (MySQL/PostgreSQL/MariaDB/MongoDB)"
        echo " 14) VPN Server (OpenVPN/WireGuard)"
        echo " 15) FTP Server"
        echo " 16) DNS Server (BIND9)"
        echo " 17) Monitoring (Prometheus/Netdata)"
        echo ""
        echo " [УПРАВЛЕНИЕ]"
        echo " 18) Удалить сервис"
        echo " 19) Показать статус установки"
        echo ""
        echo "  0) Выход"
        echo ""
        
        read -p "Выберите действие: " choice
        
        case $choice in
            1) system_update; kernel_update; read -p "Нажмите Enter..." ;;
            2) setup_timezone; setup_locale; read -p "Нажмите Enter..." ;;
            3) setup_swap; read -p "Нажмите Enter..." ;;
            4) setup_hostname; read -p "Нажмите Enter..." ;;
            5) install_base_packages; read -p "Нажмите Enter..." ;;
            6) install_fail2ban; read -p "Нажмите Enter..." ;;
            7) install_unattended_upgrades; read -p "Нажмите Enter..." ;;
            8) install_docker; read -p "Нажмите Enter..." ;;
            9) setup_git; read -p "Нажмите Enter..." ;;
            10) install_python; read -p "Нажмите Enter..." ;;
            11) deploy_web_server; read -p "Нажмите Enter..." ;;
            12) deploy_mail_server; read -p "Нажмите Enter..." ;;
            13) deploy_database; read -p "Нажмите Enter..." ;;
            14) deploy_vpn; read -p "Нажмите Enter..." ;;
            15) deploy_ftp; read -p "Нажмите Enter..." ;;
            16) deploy_dns; read -p "Нажмите Enter..." ;;
            17) deploy_monitoring; read -p "Нажмите Enter..." ;;
            18) remove_service; read -p "Нажмите Enter..." ;;
            19) show_status; read -p "Нажмите Enter..." ;;
            0) info "Завершение работы"; exit 0 ;;
            *) warn "Неверный выбор"; sleep 2 ;;
        esac
    done
}

show_status() {
    step "Статус развёртывания"
    
    echo "Установленные компоненты:"
    echo ""
    
    [[ -n "$(get_state system_updated)" ]] && echo "✓ Система обновлена: $(date -d @$(get_state system_updated) 2>/dev/null || echo 'да')"
    [[ -n "$(get_state timezone)" ]] && echo "✓ Timezone: $(get_state timezone)"
    [[ -n "$(get_state swap_size)" ]] && echo "✓ Swap: $(get_state swap_size)"
    [[ -n "$(get_state hostname)" ]] && echo "✓ Hostname: $(get_state hostname)"
    [[ -n "$(get_state fail2ban)" ]] && echo "✓ Fail2Ban установлен"
    [[ -n "$(get_state docker)" ]] && echo "✓ Docker установлен"
    [[ -n "$(get_state python_version)" ]] && echo "✓ Python: $(get_state python_version)"
    [[ -n "$(get_state web_deployed)" ]] && echo "✓ Web Server развёрнут"
    [[ -n "$(get_state mail_deployed)" ]] && echo "✓ Mail Server развёрнут"
    [[ -n "$(get_state database_deployed)" ]] && echo "✓ Database развёрнута"
    [[ -n "$(get_state vpn_deployed)" ]] && echo "✓ VPN развёрнут"
    
    echo ""
}

# ==================== ENTRY POINT ====================
main_menu
