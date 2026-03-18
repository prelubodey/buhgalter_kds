import re
import json
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# 1. Загрузка настроек из .env 
load_dotenv()

# Настройка логирования
logging.basicConfig(
    filename="bot_errors.log", 
    level=logging.ERROR, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# 2. Получение настроек из переменных окружения 
# Поддержка как TELEGRAM_TOKEN (из setup.sh), так и TELEGRAM_BOT_TOKEN
TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")

try:
    # Поддержка ALLOWED_USER_ID (из setup.sh)
    ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID") or os.getenv("TELEGRAM_CHAT_ID") or 0)
except (ValueError, TypeError):
    ALLOWED_USER_ID = 0

TRANSACTIONS_FILE = os.getenv("TRANSACTIONS_JSON_PATH", "data/transactions.json")

# Создаем папку для базы, если её нет
os.makedirs(os.path.dirname(TRANSACTIONS_FILE) or "data", exist_ok=True)

def load_data():
    if os.path.exists(TRANSACTIONS_FILE):
        try:
            with open(TRANSACTIONS_FILE, "r", encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Ошибка загрузки данных: {e}")
            return {"transactions": [], "balance": 0.0}
    return {"transactions": [], "balance": 0.0}

def save_data(data):
    try:
        with open(TRANSACTIONS_FILE, "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Ошибка сохранения данных: {e}")

# Инициализация данных
data = load_data()
current_balance = float(data.get("balance", 0))
current_transactions = data.get("transactions", [])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if ALLOWED_USER_ID != 0 and user_id != ALLOWED_USER_ID:
        await update.message.reply_text(f"Доступ запрещен. Ваш ID: {user_id}. Добавьте ALLOWED_USER_ID={user_id} в файл .env")
        return

    await update.message.reply_text(
        "Бот запущен.\n\nКоманды:\n"
        "• +300 Имя — добавить доход\n"
        "• -500 Имя — добавить расход\n"
        "• итого — получить отчет\n"
        "• обнулились — стереть все данные"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_balance, current_transactions
    
    # Проверка на то, что сообщение содержит текст (а не фото или стикер)
    if not update.message or not update.message.text:
        return

    user_id = update.message.from_user.id
    if ALLOWED_USER_ID != 0 and user_id != ALLOWED_USER_ID:
        await update.message.reply_text(f"Доступ запрещен. Ваш ID: {user_id}. Добавьте ALLOWED_USER_ID={user_id} в файл .env")
        return

    try:
        text = update.message.text.strip()
        text_lower = text.lower()

        if text_lower == "обнулились":
            current_balance = 0.0
            current_transactions = []
            save_data({"transactions": current_transactions, "balance": current_balance})
            await update.message.reply_text(f"Баланс обнулен. Текущий баланс: {current_balance}")
            return
        
        if text_lower == "итого":
            await generate_report(update, context)
            return

        # Поддержка целых чисел и чисел с плавающей точкой (в т.ч. с пробелом после знака)
        match = re.match(r'^([+-]?)\s*(\d+(?:[.,]\d+)?)\s+(.+)$', text)
        if match:
            sign = match.group(1)
            amount_str = match.group(2).replace(',', '.')
            amount = float(f"{sign}{amount_str}")
            name = match.group(3).strip()
            
            if amount.is_integer():
                amount = int(amount)
            
            # Округление для избежания проблем с точностью float
            current_balance = round(current_balance + amount, 2)
            current_transactions.append({
                "amount": amount, 
                "name": name, 
                "date": update.message.date.isoformat()
            })
            
            save_data({"transactions": current_transactions, "balance": current_balance})
            
            balance_display = int(current_balance) if float(current_balance).is_integer() else current_balance
            await update.message.reply_text(f"✅ Записано: {amount} ({name}).\nТекущий баланс: {balance_display}")
            
    except Exception as e:
        logging.error(f"Ошибка обработки сообщения: {e}")

async def generate_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_balance, current_transactions
    try:
        if not current_transactions:
            await update.message.reply_text("Нет данных для отчета.")
            return

        html_content = f"""<html>
<head><meta charset="utf-8"><title>Финансовый отчет</title></head>
<body>
<h2>Финансовый отчет</h2>
<table border='1' cellpadding='5' cellspacing='0'>
<tr><th>Сумма</th><th>Имя</th></tr>"""
        
        for t in current_transactions:
            html_content += f"<tr><td>{t['amount']}</td><td>{t['name']}</td></tr>"
        
        balance_display = int(current_balance) if float(current_balance).is_integer() else current_balance
        
        html_content += f"""</table>
<p><strong>Итоговый баланс:</strong> {balance_display}</p>
</body></html>"""

        report_file = os.path.join(os.path.dirname(TRANSACTIONS_FILE) or "data", "report.html")
        with open(report_file, "w", encoding='utf-8') as f:
            f.write(html_content)
        
        each_share = round(current_balance / 3, 2)
        each_share_display = int(each_share) if each_share.is_integer() else each_share
        
        with open(report_file, "rb") as doc:
            await update.message.reply_document(document=doc, filename="report.html")
        
        await update.message.reply_text(f"📊 Итого: {balance_display}\n👥 Каждому (на 3): {each_share_display}")
        
    except Exception as e:
        logging.error(f"Ошибка генерации отчета: {e}")
        await update.message.reply_text("Ошибка при создании отчета.")

def main():
    if not TOKEN:
        print("Ошибка: TOKEN не найден! Убедитесь, что он задан в .env файле (TELEGRAM_TOKEN или TELEGRAM_BOT_TOKEN).")
        return

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Бухгалтер запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()
