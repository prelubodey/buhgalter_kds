#!/bin/bash
echo "🚀 Установка Бухгалтера (buhgalter_kds)..."

# 1. Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "📦 Установка Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
fi

# 2. Настройка путей
PROJECT_DIR="/root/projects/buhgalter_kds"

# 3. Клонирование (Гарантированно чистая установка)
echo "📥 Загрузка кода с GitHub..."
rm -rf "$PROJECT_DIR"
git clone https://github.com/prelubodey/buhgalter_kds.git "$PROJECT_DIR"

# ПЕРЕХОДИМ В ПАПКУ ПРОЕКТА
cd "$PROJECT_DIR"

# 4. Создание структуры данных
mkdir -p data

# 5. Запрос данных для .env
echo "📝 Настройка доступа..."
# Используем /dev/tty чтобы read работал внутри curl | bash
read -p "Введите TELEGRAM_TOKEN: " tg_token < /dev/tty
read -p "Введите ALLOWED_USER_ID (ваш ID): " user_id < /dev/tty

# 6. Формирование .env
cat <<EOF > .env
TELEGRAM_TOKEN=$tg_token
ALLOWED_USER_ID=$user_id
TRANSACTIONS_JSON_PATH=data/transactions.json
EOF

# 7. Перезапись docker-compose.yml (на случай, если в репозитории старая версия)
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

# 8. Сборка и запуск
echo "🏗 Сборка и запуск контейнера..."
docker compose up -d --build

# 9. Проверка статуса
if [ "$(docker ps -q -f name=my-finance-bot)" ]; then
    echo "------------------------------------------"
    echo "✅ Бухгалтер успешно запущен!"
    echo "📊 Логи: docker logs -f my-finance-bot"
    echo "------------------------------------------"
else
    echo "❌ Ошибка при запуске. Проверьте логи: docker logs my-finance-bot"
fi