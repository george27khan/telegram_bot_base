import os
from dotenv import load_dotenv
import datetime as dt

import asyncio
from aiogram import Bot, types
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text


dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TELEGRAMM_BOT_TOKEN = os.getenv('TELEGRAMM_BOT_TOKEN')
bot = Bot(token=TELEGRAMM_BOT_TOKEN)
dp = Dispatcher(bot)

# days_in_month = 31
# map_day_to_name = {0:'Пн', 1:'Вт', 2:'Ср', 3:'Чт', 4:'Пт', 5:'Сб', 6:'Вс'}
# days_of_week_ru = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
# cur_day = dt.datetime.today().day
# day_of_week = dt.datetime.today().weekday()
# cur_day_of_week = map_day_to_name[day_of_week]
# print(cur_day, cur_day_of_week)
# #шапка календаря
# buttons = [types.InlineKeyboardButton(text=day, callback_data=f"week_day_{day}") for day in days_of_week_ru]
#
# #выравнивание календаря
# for empty in range(0, day_of_week):
#     buttons.append(types.InlineKeyboardButton(text='', callback_data=f"week_day_empty"))
#
# for day in range(1, days_in_month + 1):
#     buttons.append(types.InlineKeyboardButton(text=str(day), callback_data=f"day_{day}"))
print(dt.datetime.today().strftime("%B"))
for i in range(7):
    print((dt.datetime.today() + dt.timedelta(days=i)).strftime("%a"))
def get_calendar_keyboard():
    days_in_month = 31
    map_day_to_name = {0: 'Пн', 1: 'Вт', 2: 'Ср', 3: 'Чт', 4: 'Пт', 5: 'Сб', 6: 'Вс'}
    week_ru = {'Mon': 'Пн', 'Tue': 'Вт', 'Wed': 'Ср', 'Thu': 'Чт', 'Fri': 'Пт', 'Sat': 'Сб', 'Sun': 'Вс'}
    days_of_week_ru = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    days_of_week_en = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    month_name_en_ru = []
    cur_month_name = dt.datetime.today().strftime("%B")
    cur_day = dt.datetime.today().day
    day_of_week = dt.datetime.today().weekday()
    cur_day_of_week = map_day_to_name[day_of_week]

    print(cur_day, cur_day_of_week)
    # шапка календаря
    buttons = [types.InlineKeyboardButton(text=day, callback_data=f"week_day_{day}") for day in days_of_week_ru]

    # выравнивание календаря
    for empty in range(0, day_of_week):
        buttons.append(types.InlineKeyboardButton(text=' ', callback_data=f"week_day_empty"))

    for day in range(1, days_in_month + 1):
        buttons.append(types.InlineKeyboardButton(text=str(day), callback_data=f"day_{day}"))
    last_week_len = len(buttons) % 7
    if 0 < last_week_len < 7:
        for empty in range(0, 7 - last_week_len):
            buttons.append(types.InlineKeyboardButton(text=' ', callback_data=f"week_day_empty"))

    # Благодаря row_width=2, в первом ряду будет две кнопки, а оставшаяся одна
    # уйдёт на следующую строку
    keyboard = types.InlineKeyboardMarkup(row_width=7)
    keyboard.add(*buttons)
    return keyboard

@dp.message_handler(commands="calendar")
async def cmd_random(message: types.Message):
    await message.answer("Нажмите на кнопку, чтобы бот отправил число от 1 до 10", reply_markup=get_calendar_keyboard())

@dp.callback_query_handler(text="random_value")
async def send_random_value(call: types.CallbackQuery):
    await call.message.answer(str(randint(1, 10)))
    await call.answer(text="Спасибо, что воспользовались ботом!", show_alert=True)
    # или просто await call.answer()






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

