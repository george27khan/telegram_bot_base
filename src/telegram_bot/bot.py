import os
from dotenv import load_dotenv

import asyncio
from aiogram import Bot, types
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text


dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TELEGRAMM_BOT_TOKEN = os.getenv('TELEGRAMM_BOT_TOKEN')
bot = Bot(token=TELEGRAMM_BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ["С пюрешкой", "Без пюрешки"]
    keyboard.add(*buttons)
    await message.answer("Как подавать котлеты?", reply_markup=keyboard)
@dp.message_handler(Text(equals="С пюрешкой"))
async def with_puree(message: types.Message):
    await message.reply("Отличный выбор!")

@dp.message_handler(lambda message: message.text == "Без пюрешки")
async def without_puree(message: types.Message):
    await message.reply("Так невкусно!")

@dp.message_handler(commands="special_buttons")
async def cmd_special_buttons(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Запросить геолокацию", request_location=True))
    keyboard.add(types.KeyboardButton(text="Запросить контакт", request_contact=True))
    keyboard.add(types.KeyboardButton(text="Создать викторину",
                                      request_poll=types.KeyboardButtonPollType(type=types.PollType.QUIZ)))
    await message.answer("Выберите действие:", reply_markup=keyboard)

@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Message):
    lat = message.location.latitude
    lon = message.location.longitude
    await asyncio.sleep(10)
    reply = "latitude:  {}\nlongitude: {}".format(lat, lon)
    await message.answer(reply, reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(msg: types.Message):
    await msg.answer(f'Я бот. Приятно познакомиться, {msg.from_user.first_name}')

@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
   if msg.text.lower() == 'привет':
       await msg.answer('Привет!')
   else:
       await msg.answer('Не понимаю, что это значит.')