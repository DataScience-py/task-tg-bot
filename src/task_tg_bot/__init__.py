"""Init bot."""

import os

import dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

START_TEXT = """
Привет, %s, Я бот, который проверяет ответы на правктические задания из канала @TipoBrain

используйте команду /check и выбрите предмет, затем вам будет предложен выбор из нескольких дат, 
одну в которой будет идти проверка заданий.

"""

CHECK_TEXT = """
выберите один из слудующих предметов
"""

SUBJECTS = ["Математика", "Физика", "Информатика"]


dotenv.load_dotenv(".env")

TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")


async def start_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    start_command say hello user.

    Parameters
    ----------
    update : Update
        user_info
    context : ContextTypes.DEFAULT_TYPE
        messages
    """
    if update.message is not None and update.effective_user is not None:
        await update.message.reply_text(
            START_TEXT % (update.effective_user.full_name)
        )


async def check_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    check_command check user answer.

    Parameters
    ----------
    update : Update
        user_info
    context : ContextTypes.DEFAULT_TYPE
        messages
    """
    buttons = []
    for i in SUBJECTS:
        buttons.append(InlineKeyboardButton(i, callback_data=i))
    keyboard = [buttons]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message is not None and update.effective_user is not None:
        await update.message.reply_text(CHECK_TEXT, reply_markup=reply_markup)


async def handle_callback_query(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    if query is not None:
        await query.answer()
        if query.data == SUBJECTS[0]:
            await query.edit_message_text(text=f"Вы выбрали {SUBJECTS[0]}.")
        elif query.data == SUBJECTS[1]:
            await query.edit_message_text(text=f"Вы выбрали {SUBJECTS[1]}.")


def run_bot() -> None:
    """run_bot create a bot instance and run it."""
    global TELEGRAM_BOT_TOKEN
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("check", check_command))

    app.add_handler(CallbackQueryHandler(handle_callback_query))

    print("BOT is running")
    app.run_polling()
