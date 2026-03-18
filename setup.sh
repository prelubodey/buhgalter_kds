#!/bin/bash
echo "������ Установка Бухгалтера (buhgalter_kds)..."

# 1. Проверка Docker
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
fi

# 2. Подготовка директории
PROJECT_DIR="/root/projects/buhgalter_kds"
rm -rf "$PROJECT_DIR" # Пересоздаем, чтобы клон прошел чисто
mkdir -p "$PROJECT_DIR/data"
cd "$PROJECT_DIR"

# 3. Клонирование репозитория
echo "������ Загрузка кода с GitHub..."
git clone https://github.com/prelubodey/buhgalter_kds.git .

# 4. Запрос данных для .env
echo "������ Настройка доступа..."
read -p "Введите TELEGRAM_TOKEN: " tg_token </dev/tty
read -p "Введите ALLOWED_USER_ID (ваш ID): " user_id </dev/tty

# 5. Формирование .env
cat <<EOF > .env
TELEGRAM_TOKEN=$tg_token
ALLOWED_USER_ID=$user_id
TRANSACTIONS_JSON_PATH=data/transactions.json
EOF

# 6. Создание ПРАВИЛЬНОГО docker-compose.yml
# Монтируем папку data, чтобы база сохранялась на сервере
cat <<EOF > docker-compose.yml
services:
  finance_bot:
    build: .
    container_name: my-finance-bot
    restart: always
    env_file: .env
    volumes:
      - ./data:/app/data
EOF

# 7. Запуск
echo "������ Сборка и запуск..."
docker compose up -d --build

echo "✅ Бухгалтер успешно запущен!"
