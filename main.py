import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, types
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.utils import executor


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TELEGRAMM_BOT_TOKEN = os.getenv('TELEGRAMM_BOT_TOKEN')
bot = Bot(token=TELEGRAMM_BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(msg: types.Message):
    await msg.answer(f'Я бот. Приятно познакомиться, {msg.from_user.first_name}')

# @dp.message_handler(commands=["add_to_list"])
# async def cmd_add_to_list(message: types.Message, mylist: list[int]):
#     mylist.append(7)
#     await message.answer("Добавлено число 7")
#
# @dp.message_handler(commands=["show_list"])
# async def cmd_show_list(message: types.Message, mylist: list[int]):
#     await message.answer(f"Ваш список: {mylist}")

@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
   if msg.text.lower() == 'привет':
       await msg.answer('Привет!')
   else:
       await msg.answer('Не понимаю, что это значит.')

# Запуск процесса поллинга новых апдейтов
# async def main():
#     mylist = []
#     await dp.start_polling(bot, allowed_updates = ["mylist"])

if __name__ == '__main__':
    # mylist = []
    executor.start_polling(dp)
    # asyncio.run(main())