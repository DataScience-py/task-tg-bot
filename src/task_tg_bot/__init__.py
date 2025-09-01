"""Init bot."""

import os

import dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
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

TASKS = {
    SUBJECTS[0]: {"date": {"1": 5, "2": 5}},
    SUBJECTS[1]: {},
    SUBJECTS[2]: {},
}  # TODO: добавить взятие данных из файлов


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
    reply_markup = InlineKeyboardMarkup([buttons])

    if update.message is not None and update.effective_user is not None:
        await update.message.reply_text(CHECK_TEXT, reply_markup=reply_markup)


async def math(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.callback_query is not None:
        buttons = []
        for i in TASKS[SUBJECTS[0]].keys():
            buttons.append(InlineKeyboardButton(i, callback_data=i))
        reply_markup = InlineKeyboardMarkup([buttons])
        await update.callback_query.edit_message_text(
            text=f"Вы выбрали {SUBJECTS[0]}.", reply_markup=reply_markup
        )


async def math_date(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.callback_query is not None:
        buttons = []
        if (
            context.user_data is None
            and context.user_data.get("last_subject", None) is None
        ):
            print("Нет последней даты")
        for i in TASKS[SUBJECTS[0]][context.user_data["last_date"]].keys():
            buttons.append(InlineKeyboardButton(i, callback_data=i))
        reply_markup = InlineKeyboardMarkup([buttons])
        await update.callback_query.edit_message_text(
            text=f"Вы выбрали {SUBJECTS[0]} с датой {update.callback_query.data}.",
            reply_markup=reply_markup,
        )


async def math_task(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.effective_chat is not None:
        print("Work is None")
        chat_id = update.effective_chat.id
        await context.bot.send_message(
            chat_id=chat_id, text="Напишите ответ на задание."
        )
    print("Work")


async def handle_callback_query(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    if query is not None:
        await query.answer()
        if query.data == SUBJECTS[0]:
            if context.user_data is not None:
                context.user_data["last_subject"] = query.data
            await math(update, context)
        elif query.data == SUBJECTS[1]:
            if context.user_data is not None:
                context.user_data["last_subject"] = query.data
            await query.edit_message_text(text=f"Вы выбрали {SUBJECTS[1]}.")
        elif query.data == SUBJECTS[2]:
            if context.user_data is not None:
                context.user_data["last_subject"] = query.data
            await query.edit_message_text(text=f"Вы выбрали {SUBJECTS[2]}.")
        else:
            if (
                context.user_data is not None
                and context.user_data.get("last_subject", None) is not None
            ):
                if context.user_data["last_subject"] == SUBJECTS[0]:
                    if query.data.startswith("date"):
                        context.user_data["last_date"] = query.data
                        await math_date(update, context)
                    else:
                        context.user_data["TASK"] = query.data
                        await math_task(update, context)
                elif context.user_data["last_subject"] == SUBJECTS[1]:
                    await query.edit_message_text(
                        text=f"Вы выбрали {SUBJECTS[1]} с датой {query.data}."
                    )
                elif context.user_data["last_subject"] == SUBJECTS[2]:
                    await query.edit_message_text(
                        text=f"Вы выбрали {SUBJECTS[2]} с датой {query.data}."
                    )


async def check_task_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if (
        update.message is not None
        and context is not None
        and context.user_data is not None
        and context.user_data.get("TASK", None) is not None
    ):
        correct_answer = TASKS[context.user_data["last_subject"]][
            context.user_data["last_date"]
        ][context.user_data["TASK"]]
        print(correct_answer)
        if update.message.text is not None:
            if float(update.message.text) == float(correct_answer):
                await update.message.reply_text("Верно!")
            else:
                await update.message.reply_text("Неверно! Попробуйте еще раз.")
    print("fsd")


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
