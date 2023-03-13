import src.telegram_bot.bot as bot
from aiogram.utils import executor


if __name__ == "__main__":
    executor.start_polling(bot.dp)
