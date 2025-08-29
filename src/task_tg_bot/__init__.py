from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is not None and update.effective_user is not None:
        await update.message.reply_text(
            f"Hello {update.effective_user.first_name}"
        )


def run_bot() -> None:
    app = ApplicationBuilder().token("TOKEN").build()  # TODO: add env file

    app.add_handler(CommandHandler("hello", hello))

    print("BOT is running")
    app.run_polling()
