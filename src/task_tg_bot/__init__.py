import os

import dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

dotenv.load_dotenv(".env")

TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is not None and update.effective_user is not None:
        await update.message.reply_text(
            f"Hello {update.effective_user.first_name}"
        )


def run_bot() -> None:
    global TELEGRAM_BOT_TOKEN
    app = (
        ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    )  # TODO: add env file

    app.add_handler(CommandHandler("start", hello))

    print("BOT is running")
    app.run_polling()
