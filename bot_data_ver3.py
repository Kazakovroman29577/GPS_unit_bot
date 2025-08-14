import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, \
    ConversationHandler, ContextTypes

# Токен бота

TOKEN = 'ВАШ_ТОКЕН'

# Импорт файла данных

DATA_FILE = 'equipment_data.json'

# Константа для состояния в ConversationHandler

ASKING_IMEI = 1


# Функция для чтения данных из JSON файла

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


# Стартовая команда /start

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [

        [InlineKeyboardButton("🔎 Проверить IMEI", callback_data='check_imei')]

    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(

        "Добро пожаловать! Нажмите кнопку ниже для проверки IMEI.",

        reply_markup=reply_markup

    )


# Обработка нажатия кнопки

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    if query.data == 'check_imei':
        await query.message.reply_text("Пожалуйста, введите IMEI для поиска:")

        return ASKING_IMEI


# Обработка получения IMEI

async def receive_imei(update: Update, context: ContextTypes.DEFAULT_TYPE):
    imei_input = update.message.text.strip()

    data_list = load_data()

    found_obj = None

    for obj in data_list:

        if obj.get('imei') == imei_input:
            found_obj = obj

            break

    if found_obj:

        info = (

            f"Информация по IMEI {imei_input}:\n"

            f"Филиал: {found_obj.get('branch')}\n"

            f"Бренд: {found_obj.get('brand')}\n"

            f"Модель: {found_obj.get('model')}\n"

            f"Статус: {found_obj.get('status')}\n"

            f"Состояние: {found_obj.get('condition')}\n"

            f"Местоположение: {found_obj.get('location')}\n"

            f"Дата: {found_obj.get('date')}"

        )

    else:

        info = "Объект не найден."

    await update.message.reply_text(info)

    return ConversationHandler.END


# Обработка отмены

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Процесс отменен.')

    return ConversationHandler.END


# Основная функция запуска бота

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(

        entry_points=[CallbackQueryHandler(button)],

        states={

            ASKING_IMEI: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_imei)],

        },

        fallbacks=[CommandHandler('cancel', cancel)],

    )

    app.add_handler(CommandHandler("start", start))

    app.add_handler(conv_handler)

    app.run_polling()


if __name__ == '__main__':
    main()
