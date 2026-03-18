# 1. Используем стабильный и легкий образ
FROM python:3.10-slim

# 2. Настройка локали и кодировки (решает проблему с искаженными символами)
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# 3. Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Рабочая директория
WORKDIR /app

# 5. Копируем только requirements для эффективного кэширования слоев
# Если файла requirements.txt нет, создайте его или замените эту строку на RUN pip install...
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Копируем остальной код
COPY . .

# 7. Создаем папку для базы данных (чтобы Docker не ругался на права доступа)
RUN mkdir -p /app/data

# 8. Запуск бота
# Убедитесь, что имя файла совпадает (в прошлом сообщении был st.py, тут telegram_bot_report.py)
CMD ["python", "telegram_bot_report.py"]