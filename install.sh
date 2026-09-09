#!/bin/bash
echo "========================================"
echo "  Установка SaaS VPN Telegram Bot"
echo "========================================"

read -p "Введите токен бота (@BotFather): " BOT_TOKEN
read -p "Введите ваш Telegram ID (супер-админ): " ADMIN_ID
read -p "Введите домен для Web-панели (например, dowyanbot.vpnruss1.ru): " DOMAIN
read -p "Введите ваш логин GitHub: " GIT_USER
read -p "Введите название репозитория: " GIT_REPO

echo "[1/6] Обновление системы и установка зависимостей..."
apt-get update -y && apt-get install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git curl

echo "[2/6] Загрузка файлов проекта..."
rm -rf /opt/v1bot
git clone https://github.com/$GIT_USER/$GIT_REPO.git /opt/v1bot
chmod +x /opt/v1bot/hpwnr
chmod +x /opt/v1bot/install.sh

echo "[3/6] Настройка бота..."
sed -i "s/BOT_TOKEN = .*/BOT_TOKEN = \"$BOT_TOKEN\"/" /opt/v1bot/bot.py
sed -i "s/SUPER_ADMIN_ID = .*/SUPER_ADMIN_ID = $ADMIN_ID/" /opt/v1bot/bot.py

echo "[4/6] Установка Python-библиотек..."
python3 -m venv /opt/v1bot/venv
/opt/v1bot/venv/bin/pip install aiogram aiohttp aiosqlite requests

echo "[5/6] Настройка Nginx и SSL..."
cat << NGINX_EOF > /etc/nginx/sites-available/vpn_bot_panel
server {
    listen 80;
    server_name $DOMAIN;
    location / {
        proxy_pass http://127.0.0.1:8085;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
NGINX_EOF
ln -sf /etc/nginx/sites-available/vpn_bot_panel /etc/nginx/sites-enabled/
systemctl restart nginx
certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN

echo "[6/6] Создание и запуск службы..."
cat << SVC_EOF > /etc/systemd/system/v1bot.service
[Unit]
Description=SaaS VPN Telegram Bot
After=network.target

[Service]
User=root
WorkingDirectory=/opt/v1bot
ExecStart=/opt/v1bot/venv/bin/python3 bot.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SVC_EOF

systemctl daemon-reload
systemctl enable v1bot
systemctl start v1bot

echo "========================================"
echo "✅ Установка успешно завершена!"
echo "========================================"
