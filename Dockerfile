# 1. Используем официальный легкий образ Python
FROM python:3.10-slim

# 2. Устанавливаем системные зависимости (нужны для некоторых библиотек)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# 4. Копируем файл с зависимостями
COPY requirements.txt .

# 5. Устанавливаем библиотеки Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Копируем весь остальной код проекта в контейнер
COPY . .

# 7. Запускаем бота
CMD ["python", "telegram_bot_report.py"]