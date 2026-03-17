#!/bin/bash
echo "🚀 Установка Бухгалтера (buhgalter_kds)..."

# Проверка Docker
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
fi

mkdir -p /root/projects/buhgalter_kds
cd /root/projects/buhgalter_kds

# Клонируем, если папка пуста
if [ ! -d ".git" ]; then
    git clone https://github.com/prelubodey/buhgalter_kds.git .
fi

# Запрос данных для .env
read -p "Введите TELEGRAM_TOKEN: " tg_token </dev/tty
read -p "Введите ALLOWED_USER_ID: " user_id </dev/tty

cat <<EOF > .env
TELEGRAM_TOKEN=$tg_token
ALLOWED_USER_ID=$user_id
TRANSACTIONS_JSON_PATH=transactions.json
EOF

# Создание docker-compose.yml
cat <<EOF > docker-compose.yml
services:
  finance_bot:
    build: .
    container_name: my-finance-bot
    restart: always
    env_file: .env
    volumes:
      - ./transactions.json:/app/transactions.json
EOF

docker compose up -d --build
echo "✅ Бухгалтер запущен!"
