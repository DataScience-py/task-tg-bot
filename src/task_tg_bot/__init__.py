"""Init bot."""

# TODO: change print to loging

# imports

import json
import os
from pathlib import Path
from typing import Any

import dotenv
from pydantic import BaseModel
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
)

# load base configuration

dotenv.load_dotenv(".env")

TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

FILE_PATH: str = str(Path(__file__).parent / "data" / "tasks.json5")

with open(FILE_PATH, "r", encoding="utf-8") as f:
    temp_data: dict[str, Any] = json.load(f)


class Config(BaseModel):
    """Configuration for application."""

    START_TEXT: str = """
Привет, %s, Я бот, который проверяет ответы на правктические задания из канала @TipoBrain

используйте команду /check и выбрите предмет, затем вам будет предложен выбор из нескольких дат, 
одну в которой будет идти проверка заданий.

"""
    CHECK_TEXT: str = """
    выберите один из слудующих предметов
    """

    # LOAD JSON FILE

    SUBJECTS: list[str] = list(temp_data.keys())

    TASKS: dict[str, Any] = temp_data

    DATE_STARTING: str = "date_"

    LAST_SUBJECT: str = "LAST_SUBJECT"

    LAST_DATE: str = "LAST_DATE"


config = Config()

# Commands


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
            config.START_TEXT % update.effective_user.first_name
        )
    print("Start command is worked")


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
    for i in config.SUBJECTS:
        buttons.append(InlineKeyboardButton(i, callback_data=i))
    reply_markup = InlineKeyboardMarkup([buttons])

    if update.message is not None and update.effective_user is not None:
        await update.message.reply_text(
            config.CHECK_TEXT, reply_markup=reply_markup
        )
    print("Check command is worked")


# qery handlers


async def handle_callback_query(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    if query is not None:
        await query.answer()
        if context.user_data is None:
            print("context is None")
            return
        if query.data in config.SUBJECTS:  # Предмет
            # TODO change on funcion callback
            context.user_data[config.LAST_SUBJECT] = query.data
            await query.edit_message_text("Выберите дату для проверки заданий")
        elif str(query.data).startswith(config.DATE_STARTING):  # Дата
            if not context.user_data.get(config.LAST_SUBJECT, ""):
                if update.message is not None:
                    await update.message.reply_text("Выберите предмет")
            else:
                context.user_data[config.LAST_DATE] = query.data
                await query.edit_message_text(
                    "Выберите номер задания"
                )
        else:  # Номер задания
            if not context.user_data.get(config.LAST_SUBJECT, ""):
                if update.message is not None:
                    await update.message.reply_text("Выберите предмет")
                    return
            elif not context.user_data.get(config.LAST_DATE, ""):
                if update.message is not None:
                    await update.message.reply_text("Выберите дату")
                    return
            context.user_data["TASK"] = query.data
            if update.message is not None:
                await update.message.reply_text("Напишите ответ на задание")
    print(query)


async def check_task_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if (
        update.message is not None
        and context is not None
        and context.user_data is not None
        and context.user_data.get("TASK", None) is not None
    ):
        correct_answer = config.TASKS[context.user_data["last_subject"]][
            context.user_data["last_date"]
        ][context.user_data["TASK"]]
        if update.message.text is not None:
            if str(update.message.text) == str(correct_answer).replace(
                ".", ","
            ):
                await update.message.reply_text("Верно!")
            else:
                await update.message.reply_text("Неверно! Попробуйте еще раз.")
    else:
        if update.message is not None:
            await update.message.reply_text("Сначала выберите предмет.")
    print("check_task is worked")


def run_bot() -> None:
    """run_bot create a bot instance and run it."""
    global TELEGRAM_BOT_TOKEN
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("check", check_command))

    app.add_handler(MessageHandler(None, check_task_handler))

    app.add_handler(CallbackQueryHandler(handle_callback_query))

    print("BOT is running")
    app.run_polling()
