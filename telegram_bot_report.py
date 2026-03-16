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
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 2. Получение настроек из переменных окружения 
TOKEN = os.getenv("TELEGRAM_TOKEN")
# Преобразуем ID в int, так как из env он приходит строкой
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", 0))
# Используем путь к JSON из окружения или дефолтный в текущей папке
TRANSACTIONS_FILE = os.getenv("TRANSACTIONS_JSON_PATH", "transactions.json")

def load_data():
    if os.path.exists(TRANSACTIONS_FILE):
        try:
            with open(TRANSACTIONS_FILE, "r", encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Ошибка загрузки данных: {e}")
            return {"transactions": [], "balance": 0}
    return {"transactions": [], "balance": 0}

def save_data(data):
    try:
        with open(TRANSACTIONS_FILE, "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Ошибка сохранения данных: {e}")

# Инициализация данных
data = load_data()
current_balance = data.get("balance", 0)
current_transactions = data.get("transactions", [])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_balance, current_transactions
    
    # Проверка доступа по ID из .env 
    if update.message.from_user.id != ALLOWED_USER_ID:
        return

    try:
        text = update.message.text.lower().strip()

        if text == "обнулились":
            current_balance = 0
            current_transactions = []
            save_data({"transactions": current_transactions, "balance": current_balance})
            await update.message.reply_text(f"Баланс обнулен. Текущий баланс: {current_balance}")
            return
        
        if text == "итого":
            await generate_report(update, context)
            return

        # Парсинг транзакции (например, +300 Леша)
        match = re.match(r'([+-]?\d+)\s+(.+)', text)
        if match:
            amount = int(match.group(1))
            name = match.group(2).strip()
            
            current_balance += amount
            current_transactions.append({
                "amount": amount, 
                "name": name, 
                "date": update.message.date.isoformat()
            })
            
            save_data({"transactions": current_transactions, "balance": current_balance})
            await update.message.reply_text(f"✅ Записано: {amount} ({name}).\nТекущий баланс: {current_balance}")
            
    except Exception as e:
        logging.error(f"Ошибка обработки сообщения: {e}")

async def generate_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_balance, current_transactions
    try:
        if not current_transactions:
            await update.message.reply_text("Нет данных для отчета.")
            return

        # Генерация HTML-отчета
        html_content = f"""<html>
<head><meta charset="utf-8"><title>Финансовый отчет</title></head>
<body>
<h2>Финансовый отчет</h2>
<table border='1' cellpadding='5' cellspacing='0'>
<tr><th>Сумма</th><th>Имя</th></tr>"""
        
        for t in current_transactions:
            html_content += f"<tr><td>{t['amount']}</td><td>{t['name']}</td></tr>"
        
        html_content += f"""</table>
<p><strong>Итоговый баланс:</strong> {current_balance}</p>
</body></html>"""

        report_file = "report.html"
        with open(report_file, "w", encoding='utf-8') as f:
            f.write(html_content)
        
        each_share = round(current_balance / 3, 2)
        
        with open(report_file, "rb") as doc:
            await update.message.reply_document(document=doc, filename=report_file)
        
        await update.message.reply_text(f"📊 Итого: {current_balance}\n👥 Каждому (на 3): {each_share}")
        
    except Exception as e:
        logging.error(f"Ошибка генерации отчета: {e}")
        await update.message.reply_text("Ошибка при создании отчета.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == ALLOWED_USER_ID:
        await update.message.reply_text(
            "Бот запущен.\n\n"
            "Команды:\n"
            "• +300 Имя — добавить доход\n"
            "• -500 Имя — добавить расход\n"
            "• итого — получить отчет\n"
            "• обнулились — стереть все данные"
        )

def main():
    if not TOKEN:
        print("Ошибка: TELEGRAM_TOKEN не найден в .env файле!")
        return

    try:
        application = Application.builder().token(TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("itogo", generate_report))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("Финансовый бот запущен...")
        application.run_polling()
    except Exception as e:
        logging.error(f"Критическая ошибка запуска: {e}")

if __name__ == '__main__':
    main()