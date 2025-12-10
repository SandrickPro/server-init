#!/usr/bin/env bash
# install_nginx_certbot.sh
# Usage: sudo bash install_nginx_certbot.sh example.com you@example.com
# Assumptions: Ubuntu/Debian server with public IPv4, domain points to the server.
set -euo pipefail

if [[ $(id -u) -ne 0 ]]; then
  echo "This script must be run as root. Use sudo." >&2
  exit 1
fi

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 DOMAIN EMAIL" >&2
  echo "Example: sudo $0 example.com admin@example.com" >&2
  exit 2
fi

DOMAIN="$1"
EMAIL="$2"
WEBROOT="/var/www/$DOMAIN/html"
NGINX_CONF="/etc/nginx/sites-available/$DOMAIN"

echo "Domain: $DOMAIN"
echo "Email: $EMAIL"

# Update and install packages
apt-get update
apt-get install -y nginx certbot python3-certbot-nginx iptables iptables-persistent

# Create webroot
mkdir -p "$WEBROOT"
m -f "$WEBROOT/index.html" "$WEBROOT/unauthorized.html"
chown -R www-data:www-data "/var/www/$DOMAIN"
chmod -R 755 "/var/www/$DOMAIN"

# Create nginx server block (initial HTTP config)
cat > "$NGINX_CONF" <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;

    root $WEBROOT;
    index index.html;

    # Serve login page at /login
    location = /login {
        try_files /index.html =404;
    }

  # The authentication endpoint redirects to an error page which then
  # redirects back to /login. This shows an error and returns the user
  # to the login page instead of leaving a raw 401 response.
  location = /auth {
    # Redirect client to visible error page
    return 302 /unauthorized.html;
  }

  # Public error page that shows the message and then forwards to /login
  location = /unauthorized.html {
    try_files /unauthorized.html =404;
  }

    # Static files (css, images, etc.)
    location / {
        try_files $uri $uri/ =404;
    }
}
EOF

# Enable site
ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/$DOMAIN

# Remove default site if exists
if [ -f /etc/nginx/sites-enabled/default ]; then
  rm -f /etc/nginx/sites-enabled/default
fi

# Write the login and unauthorized pages into webroot
cat > "$WEBROOT/index.html" <<'HTML'
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Вход</title>
  <style>
    body{font-family:Arial,Helvetica,sans-serif;background:#f0f2f5;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}
    .card{background:#fff;padding:24px;border-radius:8px;box-shadow:0 6px 18px rgba(0,0,0,.08);width:320px;text-align:center}
    input{width:100%;padding:8px;margin:8px 0;border:1px solid #ccc;border-radius:4px}
    button{width:100%;padding:10px;border:0;background:#007bff;color:#fff;border-radius:4px}
    .logo{width:120px;height:120px;margin:0 auto 8px}
  </style>
</head>
<body>
  <div class="card">
    <!-- Inline SVG image shown on the login page -->
    <div class="logo">
      <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <rect width="100" height="100" rx="12" fill="#007bff" />
        <circle cx="50" cy="40" r="20" fill="#fff" />
        <rect x="30" y="65" width="40" height="8" rx="4" fill="#fff" />
      </svg>
    </div>
    <h2>Авторизация</h2>
    <form method="post" action="/auth">
      <input name="username" type="text" placeholder="Логин" autocomplete="username">
      <input name="password" type="password" placeholder="Пароль" autocomplete="current-password">
      <button type="submit">Войти</button>
    </form>
    <p style="font-size:12px;color:#666;margin-top:12px">Любые логин/пароль будут отклонены.</p>
  </div>
</body>
</html>
HTML

cat > "$WEBROOT/unauthorized.html" <<'HTML'
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Ошибка авторизации</title>
  <style>
    body{font-family:Arial,Helvetica,sans-serif;background:#fff;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}
    .wrap{text-align:center}
    img{max-width:240px}
    h1{color:#c0392b}
    a{display:inline-block;margin-top:16px;color:#007bff;text-decoration:none}
  </style>
</head>
<body>
  <div class="wrap">
    <!-- Reuse inline SVG as image -->
    <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" style="width:160px;height:160px">
      <rect width="200" height="200" rx="20" fill="#f8d7da" />
      <path d="M60 60 L140 140 M140 60 L60 140" stroke="#c0392b" stroke-width="10" stroke-linecap="round" />
    </svg>
    <h1>Ошибка авторизации</h1>
    <p>Доступ запрещён — введённые данные не принимаются.</p>
    <a href="/login">Вернуться на страницу входа</a>
  </div>
</body>
</html>
HTML

# Test nginx config and reload
nginx -t
systemctl reload nginx

# Setup iptables: allow SSH, HTTP and HTTPS
if command -v iptables >/dev/null 2>&1; then
  iptables -C INPUT -p tcp --dport 22 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 22 -j ACCEPT
  iptables -C INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 80 -j ACCEPT
  iptables -C INPUT -p tcp --dport 443 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 443 -j ACCEPT
  mkdir -p /etc/iptables && iptables-save > /etc/iptables/rules.v4
  echo "✅ iptables configured"
fi

# Obtain SSL certificate via Certbot (Let's Encrypt) using nginx plugin
# Note: domain must point to this server and TCP ports 80/443 must be reachable.
if certbot --version >/dev/null 2>&1; then
  echo "Requesting Let's Encrypt certificate for $DOMAIN..."
  certbot --nginx -n --agree-tos --redirect -m "$EMAIL" -d "$DOMAIN" || {
    echo "Certbot failed. You can try running: certbot certonly --webroot -w $WEBROOT -d $DOMAIN" >&2
    exit 0
  }
else
  echo "certbot not found after install; skipping certificate issuance." >&2
fi

echo "Installation completed. Website available at https://$DOMAIN (if certificate obtained)."

echo "Note: /auth always returns 401 so all login attempts are rejected by design."