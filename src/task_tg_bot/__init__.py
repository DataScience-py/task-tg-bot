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
if TELEGRAM_BOT_TOKEN == "":
    raise ValueError("TELEGRAM_BOT_TOKEN is not set")


ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "")
if ADMIN_PASSWORD == "":
    raise ValueError("ADMIN_PASSWORD is not set")


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

    LAST_TASK: str = "TASK"

    ADMIN: str = "ADMIN"

    admin: dict[str, Any] = {
        "level0": 0,
        "level1": 1,
        "level2": 2,
        "level3": 3,
    }


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
    reply_markup = generate_keyboard(config.SUBJECTS)
    if update.message is not None and update.effective_user is not None:
        await update.message.reply_text(
            config.CHECK_TEXT, reply_markup=reply_markup
        )
    print("Check command is worked")


async def admin_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if context.user_data is None:
        return
    context.user_data[config.ADMIN] = (
        config.admin["level1"]
        if context.user_data.get(config.ADMIN, config.admin["level0"])
        == config.admin["level0"]
        else config.admin["level0"]
    )
    if (
        update.message is not None
        and context.user_data[config.ADMIN] == config.admin["level1"]
    ):
        await update.message.reply_text("Введите пароль")
    print("admin_command is worked")


def generate_keyboard(objects: list[Any]) -> InlineKeyboardMarkup:
    """Generate keyboard for callback query."""
    keyboard = []
    row = []
    for item in objects:
        row.append(InlineKeyboardButton(item, callback_data=item))
        if len(row) == 8:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup([keyboard])


# qery handlers


async def handle_callback_query(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """handle_callback_query handle callback query."""
    query = update.callback_query
    if query is not None:
        await query.answer()
        if query.data in config.SUBJECTS:  # Предмет
            await subject(update=update, context=context)
        elif str(query.data).startswith(config.DATE_STARTING):  # Дата
            await date(update=update, context=context)
        else:  # Номер задания
            await task(update=update, context=context)


async def subject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Subject choice subject."""
    if context.user_data is None:
        print("context is None")
        return
    query = update.callback_query
    if query is None:
        print("query is None")
        return
    context.user_data[config.LAST_SUBJECT] = query.data
    reply_markup = generate_keyboard(
        config.TASKS[context.user_data[config.LAST_SUBJECT]].keys()
    )
    await query.edit_message_text("Выберите дату для проверки заданий")
    await query.edit_message_reply_markup(reply_markup)
    print("subject is worked")


async def date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Date choice date."""
    if context.user_data is None:
        return
    query = update.callback_query
    if query is None:
        return
    if not context.user_data.get(config.LAST_SUBJECT, ""):
        await query.edit_message_text("Сначала выберите предмет.")
        reply_markup = generate_keyboard(config.SUBJECTS)
        await query.edit_message_reply_markup(reply_markup)
        return
    context.user_data[config.LAST_DATE] = query.data
    reply_markup = generate_keyboard(
        config.TASKS[context.user_data[config.LAST_SUBJECT]][
            context.user_data[config.LAST_DATE]
        ].keys()
    )
    await query.edit_message_text("Выберите номер задания")
    await query.edit_message_reply_markup(reply_markup)


async def task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Task choice task."""
    if context.user_data is None:
        return
    query = update.callback_query
    if query is None:
        return
    if not context.user_data.get(config.LAST_SUBJECT, ""):
        await query.edit_message_text("Сначала выберите предмет.")
        reply_markup = generate_keyboard(config.SUBJECTS)
        await query.edit_message_reply_markup(reply_markup)
        return
    if not context.user_data.get(config.LAST_DATE, ""):
        await query.edit_message_text("Сначала выберите дату.")
        reply_markup = generate_keyboard(
            config.TASKS[context.user_data[config.LAST_SUBJECT]].keys()
        )
        await query.edit_message_reply_markup(reply_markup)
        return
    context.user_data[config.LAST_TASK] = query.data
    if update.callback_query is None:
        return
    if update.callback_query is not None:
        return
    chat_id = update.callback_query.message.chat_id
    await context.bot.send_message(
        chat_id=chat_id, text="Напишите ответ на задание"
    )


async def check_task_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """check_task_handler check user answer."""
    if context.user_data is not None:
        admin_level = context.user_data.get(
            config.ADMIN, config.admin["level0"]
        )
        if admin_level == config.admin["level1"]:
            if update.message is not None and update.message.text is not None:
                user_pw = update.message.text
                if user_pw == ADMIN_PASSWORD:
                    context.user_data[config.ADMIN] = config.admin["level2"]
                else:
                    context.user_data[config.ADMIN] = config.admin["level0"]
                print("Admin is worked", context.user_data[config.ADMIN])
        if admin_level == config.admin["level2"]:
            print("Work 2 level")
            if update.message and update.message.document is not None:
                document = update.message.document

                if document.mime_type == "application/json":
                    # Загружаем файл
                    file = await context.bot.get_file(document.file_id)

                    # Скачиваем содержимое файла в байтах
                    file_bytes = await file.download_as_bytearray()

                    # Декодируем байты в строку, используя UTF-8
                    json_string = file_bytes.decode("utf-8")
                    # Шаг 2: Десериализация JSON
                    try:
                        # Преобразуем JSON-строку в Python-объект (словарь, список и т.д.)
                        json_object = json.loads(json_string)
                        # Теперь вы можете работать с json_object как с обычным Python-объектом
                        await update.message.reply_text(
                            "Файл успешно обработан."
                        )
                        load_new_task(json_object)

                    except json.JSONDecodeError:
                        await update.message.reply_text(
                            "Ошибка при парсинге JSON файла."
                        )
                else:
                    await update.message.reply_text(
                        "Пожалуйста, отправьте файл в формате JSON."
                    )
    if (
        update.message is not None
        and context is not None
        and context.user_data is not None
        and context.user_data.get(config.LAST_TASK, None) is not None
    ):
        correct_answer = config.TASKS[context.user_data[config.LAST_SUBJECT]][
            context.user_data[config.LAST_DATE]
        ][context.user_data[config.LAST_TASK]]
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


def load_new_task(js: dict[str, Any]) -> None:
    for name_subject, value in js.items():
        for date, task in value.items():
            if not date.startswith(config.DATE_STARTING):
                date = config.DATE_STARTING + date
            if config.TASKS.get(name_subject, None) is not None:
                config.TASKS[name_subject][date] = task
            else:
                config.TASKS[name_subject] = {date: task}
    config.SUBJECTS = list(config.TASKS.keys())
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(config.TASKS, f, indent=4, ensure_ascii=False)
    print("New task is loaded")


def run_bot() -> None:
    """run_bot create a bot instance and run it."""
    global TELEGRAM_BOT_TOKEN
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("check", check_command))
    app.add_handler(CommandHandler("admin", admin_command))

    app.add_handler(MessageHandler(None, check_task_handler))

    app.add_handler(CallbackQueryHandler(handle_callback_query))

    print("BOT is running")
    app.run_polling()
