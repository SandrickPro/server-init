#!/bin/bash
################################################################################
# Web Deploy Advanced Module
# Автор: Sandrick Tech
# Дата: 2024-12-09
# Описание: Модуль развёртывания веб-сервисов с прогрессивной авторизацией
################################################################################

set -euo pipefail

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Глобальные переменные
WWW_DIR="/srv/www"
NGINX_SITES_AVAILABLE="/etc/nginx/sites-available"
NGINX_SITES_ENABLED="/etc/nginx/sites-enabled"
AUTH_LOG="/srv/sys/logs/web-auth.log"
AUTH_DB="/srv/sys/.web_auth_attempts.json"

################################################################################
# УТИЛИТЫ
################################################################################

info() { 
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() { 
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() { 
    echo -e "${RED}[ERROR]${NC} $1"
}

step() { 
    echo -e "${CYAN}[STEP]${NC} $1"
}

################################################################################
# УСТАНОВКА NGINX С МОДУЛЯМИ
################################################################################

install_nginx_full() {
    step "Установка Nginx с дополнительными модулями..."
    
    # Добавляем PPA для последней версии Nginx
    add-apt-repository -y ppa:nginx/stable 2>/dev/null || true
    apt-get update -qq
    
    # Устанавливаем Nginx и модули
    apt-get install -y \
        nginx \
        nginx-extras \
        libnginx-mod-http-geoip \
        libnginx-mod-http-headers-more-filter \
        libnginx-mod-http-cache-purge \
        libnginx-mod-http-ndk \
        libnginx-mod-http-lua \
        certbot \
        python3-certbot-nginx \
        php-fpm \
        php-mysql \
        php-curl \
        php-gd \
        php-mbstring \
        php-xml \
        php-xmlrpc \
        php-soap \
        php-intl \
        php-zip
    
    # Создаём директории
    mkdir -p "$WWW_DIR"/{html,auth-site,wordpress}
    mkdir -p /var/log/nginx/sites
    
    # Настраиваем основной конфиг Nginx
    configure_nginx_main
    
    # Запускаем Nginx
    systemctl enable nginx
    systemctl start nginx
    
    info "✅ Nginx установлен и запущен"
}

configure_nginx_main() {
    step "Настройка главного конфига Nginx..."
    
    cat > /etc/nginx/nginx.conf <<'NGINX_EOF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;
error_log /var/log/nginx/error.log;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 2048;
    use epoll;
    multi_accept on;
}

http {
    ##
    # Basic Settings
    ##
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    ##
    # SSL Settings
    ##
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    ##
    # Logging Settings
    ##
    access_log /var/log/nginx/access.log;
    
    ##
    # Gzip Settings
    ##
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/rss+xml font/truetype font/opentype 
               application/vnd.ms-fontobject image/svg+xml;
    
    ##
    # Rate Limiting
    ##
    limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;
    limit_conn_zone $binary_remote_addr zone=addr:10m;
    
    ##
    # Virtual Host Configs
    ##
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
NGINX_EOF
    
    info "Главный конфиг Nginx настроен"
}

################################################################################
# СОЗДАНИЕ САЙТА С ПРОГРЕССИВНОЙ АВТОРИЗАЦИЕЙ
################################################################################

create_auth_site() {
    local domain="${1:-auth.local}"
    local port="${2:-8080}"
    
    step "Создание сайта с прогрессивной авторизацией..."
    
    # Создаём структуру
    local site_dir="$WWW_DIR/auth-site"
    mkdir -p "$site_dir"/{public,includes,logs}
    
    # Инициализируем БД попыток авторизации
    if [[ ! -f "$AUTH_DB" ]]; then
        echo '{"attempts": {}}' > "$AUTH_DB"
        chmod 600 "$AUTH_DB"
    fi
    
    # Создаём красивую страницу авторизации с фоном
    create_auth_page "$site_dir"
    
    # Создаём обработчик авторизации
    create_auth_handler "$site_dir"
    
    # Создаём страницу ошибки
    create_error_page "$site_dir"
    
    # Настраиваем Nginx для этого сайта
    configure_nginx_auth_site "$domain" "$port" "$site_dir"
    
    # Настраиваем PHP-FPM
    configure_php_fpm
    
    info "✅ Сайт авторизации создан: http://$domain:$port"
}

create_auth_page() {
    local site_dir="$1"
    
    cat > "$site_dir/public/index.html" <<'AUTH_HTML'
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Login</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            height: 100vh;
            overflow: hidden;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }
        
        /* Анимированный фон */
        .background {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* Плавающие элементы */
        .floating-shapes {
            position: absolute;
            width: 100%;
            height: 100%;
            overflow: hidden;
            z-index: 1;
        }
        
        .shape {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.1);
            animation: float 20s infinite ease-in-out;
        }
        
        .shape:nth-child(1) {
            width: 80px;
            height: 80px;
            top: 10%;
            left: 20%;
            animation-delay: 0s;
        }
        
        .shape:nth-child(2) {
            width: 120px;
            height: 120px;
            top: 60%;
            left: 80%;
            animation-delay: 2s;
        }
        
        .shape:nth-child(3) {
            width: 60px;
            height: 60px;
            top: 80%;
            left: 10%;
            animation-delay: 4s;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            50% { transform: translateY(-30px) rotate(180deg); }
        }
        
        /* Контейнер формы */
        .login-container {
            position: relative;
            z-index: 2;
            background: rgba(255, 255, 255, 0.95);
            padding: 40px 50px;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
            width: 400px;
            max-width: 90%;
            backdrop-filter: blur(10px);
            animation: slideIn 0.5s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-50px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .login-header h1 {
            color: #333;
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .login-header p {
            color: #666;
            font-size: 14px;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-group label {
            display: block;
            color: #555;
            margin-bottom: 8px;
            font-weight: 500;
        }
        
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s;
            background: #f9f9f9;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
            background: white;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .submit-btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 10px;
            color: white;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .submit-btn:active {
            transform: translateY(0);
        }
        
        .submit-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        .cooldown-message {
            display: none;
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
            text-align: center;
            color: #856404;
        }
        
        .cooldown-message.active {
            display: block;
            animation: shake 0.5s;
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }
        
        .timer {
            font-size: 24px;
            font-weight: bold;
            color: #dc3545;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="background"></div>
    
    <div class="floating-shapes">
        <div class="shape"></div>
        <div class="shape"></div>
        <div class="shape"></div>
    </div>
    
    <div class="login-container">
        <div class="login-header">
            <h1>🔐 Вход в систему</h1>
            <p>Введите учётные данные</p>
        </div>
        
        <form id="loginForm" action="/auth/login.php" method="POST">
            <div class="form-group">
                <label for="username">Имя пользователя</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">Пароль</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="submit-btn" id="submitBtn">Войти</button>
        </form>
        
        <div class="cooldown-message" id="cooldownMessage">
            <p>⏰ Превышено количество попыток</p>
            <p>Попробуйте снова через:</p>
            <div class="timer" id="timer">00:00</div>
        </div>
    </div>
    
    <script>
        // Проверка состояния cooldown при загрузке
        const checkCooldown = () => {
            const cooldownEnd = localStorage.getItem('cooldownEnd');
            if (cooldownEnd) {
                const remaining = Math.max(0, parseInt(cooldownEnd) - Date.now());
                if (remaining > 0) {
                    startCooldown(remaining);
                    return true;
                } else {
                    localStorage.removeItem('cooldownEnd');
                }
            }
            return false;
        };
        
        const startCooldown = (milliseconds) => {
            const form = document.getElementById('loginForm');
            const submitBtn = document.getElementById('submitBtn');
            const cooldownMsg = document.getElementById('cooldownMessage');
            const timer = document.getElementById('timer');
            
            form.style.display = 'none';
            cooldownMsg.classList.add('active');
            submitBtn.disabled = true;
            
            const endTime = Date.now() + milliseconds;
            localStorage.setItem('cooldownEnd', endTime);
            
            const updateTimer = () => {
                const remaining = Math.max(0, endTime - Date.now());
                
                if (remaining === 0) {
                    form.style.display = 'block';
                    cooldownMsg.classList.remove('active');
                    submitBtn.disabled = false;
                    localStorage.removeItem('cooldownEnd');
                    return;
                }
                
                const seconds = Math.floor(remaining / 1000);
                const minutes = Math.floor(seconds / 60);
                const secs = seconds % 60;
                
                timer.textContent = `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
                setTimeout(updateTimer, 1000);
            };
            
            updateTimer();
        };
        
        // Проверяем при загрузке
        checkCooldown();
        
        // Обработка отправки формы
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            
            try {
                const response = await fetch('/auth/login.php', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.cooldown) {
                    startCooldown(data.cooldown * 1000);
                } else if (data.success) {
                    window.location.href = data.redirect || '/dashboard';
                } else {
                    alert(data.message || 'Ошибка авторизации');
                }
            } catch (error) {
                alert('Ошибка соединения с сервером');
            }
        });
    </script>
</body>
</html>
AUTH_HTML
    
    info "Страница авторизации создана"
}

create_auth_handler() {
    local site_dir="$1"
    
    mkdir -p "$site_dir/public/auth"
    
    cat > "$site_dir/public/auth/login.php" <<'PHP_EOF'
<?php
header('Content-Type: application/json');

$auth_db = '/srv/sys/.web_auth_attempts.json';
$auth_log = '/srv/sys/logs/web-auth.log';

// Функция логирования
function log_auth($message) {
    global $auth_log;
    $timestamp = date('Y-m-d H:i:s');
    $ip = $_SERVER['REMOTE_ADDR'];
    file_put_contents($auth_log, "[$timestamp] [$ip] $message\n", FILE_APPEND);
}

// Загрузка БД попыток
$db = json_decode(file_get_contents($auth_db), true);
if (!$db) {
    $db = ['attempts' => []];
}

$ip = $_SERVER['REMOTE_ADDR'];
$current_time = time();

// Проверяем существующие попытки для этого IP
if (!isset($db['attempts'][$ip])) {
    $db['attempts'][$ip] = [
        'count' => 0,
        'last_attempt' => 0,
        'cooldown_until' => 0
    ];
}

$attempts = &$db['attempts'][$ip];

// Проверяем активный cooldown
if ($attempts['cooldown_until'] > $current_time) {
    $cooldown = $attempts['cooldown_until'] - $current_time;
    log_auth("Попытка входа во время cooldown (осталось ${cooldown}с)");
    
    echo json_encode([
        'success' => false,
        'cooldown' => $cooldown,
        'message' => 'Слишком много попыток. Подождите.'
    ]);
    exit;
}

// Сброс счётчика если прошло более 1 часа
if ($current_time - $attempts['last_attempt'] > 3600) {
    $attempts['count'] = 0;
}

// Увеличиваем счётчик попыток
$attempts['count']++;
$attempts['last_attempt'] = $current_time;

// Прогрессивное увеличение времени блокировки
$cooldown_times = [5, 15, 30, 60, 120, 300, 600, 1800, 3600];
$attempt_index = min($attempts['count'] - 1, count($cooldown_times) - 1);
$cooldown = $cooldown_times[$attempt_index];

$attempts['cooldown_until'] = $current_time + $cooldown;

// Сохраняем БД
file_put_contents($auth_db, json_encode($db, JSON_PRETTY_PRINT));

// Логируем попытку
$username = $_POST['username'] ?? 'unknown';
log_auth("Неудачная попытка входа (попытка #{$attempts['count']}, cooldown: ${cooldown}с, user: $username)");

// Возвращаем ошибку с cooldown
echo json_encode([
    'success' => false,
    'cooldown' => $cooldown,
    'attempt' => $attempts['count'],
    'message' => 'Неверные учётные данные. Cooldown: ' . $cooldown . ' секунд.'
]);
?>
PHP_EOF
    
    chmod 755 "$site_dir/public/auth/login.php"
    info "Обработчик авторизации создан"
}

create_error_page() {
    local site_dir="$1"
    
    cat > "$site_dir/public/error.html" <<'ERROR_HTML'
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ошибка авторизации</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .error-container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        h1 {
            color: #ff6b6b;
            font-size: 48px;
            margin: 0 0 20px 0;
        }
        p {
            color: #666;
            font-size: 18px;
        }
        a {
            display: inline-block;
            margin-top: 20px;
            padding: 12px 30px;
            background: #ff6b6b;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            transition: background 0.3s;
        }
        a:hover {
            background: #ee5a6f;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>❌ Ошибка</h1>
        <p>Неверные учётные данные</p>
        <p>Пожалуйста, попробуйте снова</p>
        <a href="/">Вернуться к авторизации</a>
    </div>
</body>
</html>
ERROR_HTML
    
    info "Страница ошибки создана"
}

configure_nginx_auth_site() {
    local domain="$1"
    local port="$2"
    local site_dir="$3"
    
    cat > "$NGINX_SITES_AVAILABLE/$domain.conf" <<NGINX_SITE
server {
    listen $port;
    server_name $domain;
    
    root $site_dir/public;
    index index.html index.php;
    
    access_log $site_dir/logs/access.log;
    error_log $site_dir/logs/error.log;
    
    # Rate limiting
    limit_req zone=one burst=5 nodelay;
    limit_conn addr 10;
    
    location / {
        try_files \$uri \$uri/ =404;
    }
    
    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php-fpm.sock;
        fastcgi_param SCRIPT_FILENAME \$document_root\$fastcgi_script_name;
        include fastcgi_params;
    }
    
    # Защита от hotlinking
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        valid_referers none blocked $domain;
        if (\$invalid_referer) {
            return 403;
        }
    }
}
NGINX_SITE
    
    ln -sf "$NGINX_SITES_AVAILABLE/$domain.conf" "$NGINX_SITES_ENABLED/"
    
    nginx -t && systemctl reload nginx
    
    info "Nginx сайт настроен: http://$domain:$port"
}

configure_php_fpm() {
    step "Настройка PHP-FPM..."
    
    # Находим версию PHP
    local php_version=$(php -v | head -1 | awk '{print $2}' | cut -d'.' -f1,2)
    
    # Оптимизируем конфиг PHP-FPM
    cat > "/etc/php/$php_version/fpm/pool.d/www.conf" <<'PHP_FPM'
[www]
user = www-data
group = www-data
listen = /var/run/php/php-fpm.sock
listen.owner = www-data
listen.group = www-data
pm = dynamic
pm.max_children = 50
pm.start_servers = 5
pm.min_spare_servers = 5
pm.max_spare_servers = 35
pm.max_requests = 500
PHP_FPM
    
    systemctl restart php${php_version}-fpm
    
    info "PHP-FPM настроен"
}

################################################################################
# УСТАНОВКА WORDPRESS
################################################################################

install_wordpress() {
    local domain="${1:-wordpress.local}"
    local db_name="${2:-wordpress}"
    local db_user="${3:-wp_user}"
    local db_pass="${4:-$(openssl rand -base64 16)}"
    
    step "Установка WordPress..."
    
    local wp_dir="$WWW_DIR/wordpress"
    
    # Скачиваем WordPress
    cd /tmp
    wget -q https://wordpress.org/latest.tar.gz
    tar -xzf latest.tar.gz
    mv wordpress "$wp_dir"
    rm latest.tar.gz
    
    # Создаём БД MySQL
    create_wordpress_database "$db_name" "$db_user" "$db_pass"
    
    # Настраиваем wp-config.php
    configure_wordpress "$wp_dir" "$db_name" "$db_user" "$db_pass"
    
    # Настраиваем Nginx для WordPress
    configure_nginx_wordpress "$domain" "$wp_dir"
    
    # Права доступа
    chown -R www-data:www-data "$wp_dir"
    find "$wp_dir" -type d -exec chmod 755 {} \;
    find "$wp_dir" -type f -exec chmod 644 {} \;
    
    info "✅ WordPress установлен: http://$domain"
    info "База данных: $db_name"
    info "Пользователь БД: $db_user"
    info "Пароль БД: $db_pass"
}

create_wordpress_database() {
    local db_name="$1"
    local db_user="$2"
    local db_pass="$3"
    
    mysql -e "CREATE DATABASE IF NOT EXISTS $db_name DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    mysql -e "CREATE USER IF NOT EXISTS '$db_user'@'localhost' IDENTIFIED BY '$db_pass';"
    mysql -e "GRANT ALL PRIVILEGES ON $db_name.* TO '$db_user'@'localhost';"
    mysql -e "FLUSH PRIVILEGES;"
    
    info "База данных WordPress создана"
}

configure_wordpress() {
    local wp_dir="$1"
    local db_name="$2"
    local db_user="$3"
    local db_pass="$4"
    
    cp "$wp_dir/wp-config-sample.php" "$wp_dir/wp-config.php"
    
    # Генерируем соли
    local salts=$(curl -s https://api.wordpress.org/secret-key/1.1/salt/)
    
    sed -i "s/database_name_here/$db_name/" "$wp_dir/wp-config.php"
    sed -i "s/username_here/$db_user/" "$wp_dir/wp-config.php"
    sed -i "s/password_here/$db_pass/" "$wp_dir/wp-config.php"
    
    # Заменяем соли
    sed -i "/AUTH_KEY/,/NONCE_SALT/d" "$wp_dir/wp-config.php"
    sed -i "/table_prefix/i $salts" "$wp_dir/wp-config.php"
    
    info "WordPress настроен"
}

configure_nginx_wordpress() {
    local domain="$1"
    local wp_dir="$2"
    
    cat > "$NGINX_SITES_AVAILABLE/$domain.conf" <<NGINX_WP
server {
    listen 80;
    server_name $domain;
    
    root $wp_dir;
    index index.php index.html;
    
    access_log /var/log/nginx/sites/${domain}-access.log;
    error_log /var/log/nginx/sites/${domain}-error.log;
    
    client_max_body_size 64M;
    
    location / {
        try_files \$uri \$uri/ /index.php?\$args;
    }
    
    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php-fpm.sock;
        fastcgi_param SCRIPT_FILENAME \$document_root\$fastcgi_script_name;
        include fastcgi_params;
    }
    
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires max;
        log_not_found off;
    }
    
    location = /favicon.ico {
        log_not_found off;
        access_log off;
    }
    
    location = /robots.txt {
        allow all;
        log_not_found off;
        access_log off;
    }
    
    location ~ /\.ht {
        deny all;
    }
}
NGINX_WP
    
    ln -sf "$NGINX_SITES_AVAILABLE/$domain.conf" "$NGINX_SITES_ENABLED/"
    nginx -t && systemctl reload nginx
    
    info "Nginx конфиг для WordPress создан"
}

################################################################################
# ГЛАВНОЕ МЕНЮ
################################################################################

web_deploy_menu() {
    while true; do
        local choice=$(dialog --clear \
            --backtitle "Web Deploy Advanced" \
            --title "Развёртывание веб-сервисов" \
            --menu "Выберите действие:" \
            20 70 10 \
            1 "🌐 Установить Nginx (полная)" \
            2 "🔐 Создать сайт с прогрессивной авторизацией" \
            3 "📝 Установить WordPress" \
            4 "📄 Создать простую статическую страницу" \
            5 "🔒 Настроить SSL (Let's Encrypt)" \
            6 "📊 Показать статус Nginx" \
            0 "◀ Назад" \
            3>&1 1>&2 2>&3)
        
        case $choice in
            1) install_nginx_full ;;
            2) 
                local domain=$(dialog --inputbox "Домен (или auth.local):" 8 50 "auth.local" 3>&1 1>&2 2>&3)
                local port=$(dialog --inputbox "Порт:" 8 50 "8080" 3>&1 1>&2 2>&3)
                create_auth_site "$domain" "$port"
                dialog --msgbox "Сайт авторизации создан!\nURL: http://$domain:$port" 10 50
                ;;
            3)
                local domain=$(dialog --inputbox "Домен для WordPress:" 8 50 "wordpress.local" 3>&1 1>&2 2>&3)
                install_wordpress "$domain"
                dialog --msgbox "WordPress установлен!\nURL: http://$domain\nЗавершите установку в браузере" 10 50
                ;;
            4)
                dialog --msgbox "Функция в разработке" 8 40
                ;;
            5)
                dialog --msgbox "Функция в разработке" 8 40
                ;;
            6)
                systemctl status nginx > /tmp/nginx_status.txt
                dialog --textbox /tmp/nginx_status.txt 20 70
                ;;
            0|"") return ;;
        esac
    done
}

# Если запущен напрямую
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $EUID -ne 0 ]]; then
        echo "Требуются права root"
        exit 1
    fi
    web_deploy_menu
fi
