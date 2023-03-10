import os
from dotenv import load_dotenv
import datetime as dt
from dateutil.relativedelta import relativedelta
import calendar
import json
import logging

import asyncio
from aiogram import Bot, types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text

from aiogram.dispatcher.filters.state import State, StatesGroup

from src.database import engine, Session
from src.database import Setting


from sqlalchemy import Engine
from sqlalchemy import (
    create_engine,
    insert,
    MetaData,
    Table,
    String,
    Time,
    Integer,
    Numeric,
    Column,
    DateTime,
    Boolean,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy.sql import func

g_hour_start_d = {'Mon': 9, 'Tue': 9, 'Wed': 9, 'Thu': 9, 'Fri': 9, 'Sat': 9, 'Sun': 9}
g_hour_end_d = {'Mon': 18, 'Tue': 18, 'Wed': 18, 'Thu': 18, 'Fri': 18, 'Sat': 18, 'Sun': 18}
g_session_time = 0.25
logging.basicConfig(level=logging.INFO)

def load_settings():
    global g_hour_start_d, g_hour_end_d, g_session_time
    with Session() as session:
        g_hour_start_d = json.loads(session.get(Setting, "start_hour_scheduler").json_value)
        g_hour_end_d = json.loads(session.get(Setting, "end_hour_scheduler").json_value)
        g_session_time = session.get(Setting, "session_time_hour").number_value
load_settings()

def get_time_format(hour: float) -> str:
    return f'{int(hour // 1)}:{int(hour % 1 * 60):02}'

dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TELEGRAMM_BOT_TOKEN = os.getenv('TELEGRAMM_BOT_TOKEN')
bot = Bot(token=TELEGRAMM_BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class Booking(StatesGroup):
    choose_day = State()
    choose_time = State()

def get_time_keyboard(chosen_date: dt.datetime):
    buttons = []
    cur_day_name = chosen_date.strftime("%a")
    start_hour = g_hour_start_d[cur_day_name]
    end_hour = g_hour_end_d[cur_day_name]
    start_time = chosen_date.replace(hour=int(start_hour), minute=int((start_hour % 1) * 60))
    end_time = chosen_date.replace(hour=int(end_hour), minute=int((end_hour % 1) * 60))
    while start_time < end_time:
        next_time = start_time + dt.timedelta(hours=int(g_session_time), minutes=int((g_session_time % 1) * 60))
        button_text = f"{start_time.strftime('''%H:%M''')}-{next_time.strftime('''%H:%M''')}"
        buttons.append(types.InlineKeyboardButton(text=button_text, callback_data=f"time_{button_text}",
                                                  start_time = str(start_time),
                                                  end_time = str(end_time)))
        start_time = next_time
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    keyboard.add(*buttons)
    return keyboard

def get_calendar_keyboard(base_date: dt.date) -> types.InlineKeyboardMarkup:
    lang = 'en'
    max_calendar_month = 2
    current_month = dt.date.today().month
    days_in_month = calendar.monthrange(base_date.year, base_date.month)[1]
    first_month_date = base_date.replace(day=1)
    dates_of_month = [first_month_date + dt.timedelta(day) for day in range(days_in_month)]
    map_day_to_name_ru = {1: 'Пн', 2: 'Вт', 3: 'Ср', 4: 'Чт', 5: 'Пт', 6: 'Сб', 7: 'Вс'}
    map_day_to_name_en = {1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat', 7: 'Sun'}
    week_ru = {'Mon': 'Пн', 'Tue': 'Вт', 'Wed': 'Ср', 'Thu': 'Чт', 'Fri': 'Пт', 'Sat': 'Сб', 'Sun': 'Вс'}

    days_of_week = list(g_hour_start_d.keys())
    cur_month_name = base_date.strftime("%B")
    cur_day = base_date.day

    # шапка календаря
    buttons = [types.InlineKeyboardButton(text=day_name, callback_data=f"week_day_{day}") for day, day_name in enumerate(days_of_week)]

    # выравнивание календаря в начале
    for empty in range(0, first_month_date.weekday()):
        buttons.append(types.InlineKeyboardButton(text=' ', callback_data=f"empty_day"))

    for day, date in enumerate(dates_of_month):
        if date < dt.date.today():
            buttons.append(types.InlineKeyboardButton(text=str(day + 1), callback_data=f"empty_day"))
        else:
            buttons.append(types.InlineKeyboardButton(text=str(day + 1), callback_data=f"day_{date.strftime('''%d.%m.%Y''')}" ))

    # выравнивание календаря в конце
    last_week_len = len(buttons) % 7
    if 0 < last_week_len < 7:
        for empty in range(0, 7 - last_week_len):
            buttons.append(types.InlineKeyboardButton(text=' ', callback_data=f"empty_day"))
    if base_date.month > current_month:
        buttons.append(types.InlineKeyboardButton(text='предыдущий месяц', callback_data=f"prev_month"))
    if base_date.month < current_month + max_calendar_month:
        buttons.append(types.InlineKeyboardButton(text='следующий месяц', callback_data=f"next_month"))
    keyboard = types.InlineKeyboardMarkup(row_width=7)
    keyboard.add(*buttons)
    return keyboard

@dp.callback_query_handler(Text(startswith=["next_month"]), state=Booking.choose_day)
async def make_calendar_next(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    next_date = state_data['state_current_date'] + relativedelta(months=1)
    await call.message.answer("Выберите дату для бронирования", reply_markup=get_calendar_keyboard(next_date))
    await state.update_data(state_current_date=next_date)
    await call.answer()

@dp.callback_query_handler(Text(startswith=["prev_month"]), state=Booking.choose_day)
async def make_calendar_prev(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    prev_date = state_data['state_current_date'] - relativedelta(months=1)
    await call.message.answer("Выберите дату для бронирования", reply_markup=get_calendar_keyboard(prev_date))
    await state.update_data(state_current_date=prev_date)
    await call.answer()

@dp.message_handler(commands="calendar")
async def make_calendar(message: types.Message, state: FSMContext):
    await message.answer("Выберите дату для бронирования", reply_markup=get_calendar_keyboard(dt.date.today()))
    await state.update_data(state_current_date=dt.date.today())
    await Booking.choose_day.set()  # встаем в состояние выбора дня

@dp.callback_query_handler(Text(startswith=["empty_day"]), state=Booking.choose_day)
async def callback_empty(call: types.CallbackQuery):
    await call.answer()

@dp.callback_query_handler(Text(startswith=["day_"]), state=Booking.choose_day)
async def callback_choose_day(call: types.CallbackQuery, state: FSMContext):
    button_datetime = dt.datetime.strptime(call.data[4:], '''%d.%m.%Y''')
    print(button_datetime)
    await Booking.choose_time.set()  # встаем в состояние выбора дня
    await call.message.answer("Выберите время для бронирования", reply_markup=get_time_keyboard(button_datetime))
@dp.callback_query_handler(Text(startswith=["time_"]), state=Booking.choose_time)
async def callback_choose_time(call: types.CallbackQuery, state: FSMContext):
    button_datetime = dt.datetime.strptime(call.data[4:], '''%d.%m.%Y''')
    print(button_datetime)
    await Booking.choose_time.set()  # встаем в состояние выбора дня
    await call.message.answer("Выберите время для бронирования", reply_markup=get_time_keyboard(button_datetime))

@dp.message_handler(state=Booking.choose_day.state)
async def get_day(message: types.Message, state: FSMContext):
    print(1)
    await message.answer('Напиши текст рассылки1')
    print(message.text.lower())
    if message.text.lower() not in 'week_day_10':
        await message.answer("Пожалуйста, выберите другую дату")
        return
    await state.update_data(chosen_day=message.text.lower())

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for size in [1, 2, 3]:
        keyboard.add(size)
    await state.set_state(Booking.choose_time.state)
    await message.answer("Теперь выберите время записи:", reply_markup=keyboard)

#
# class UserState(StatesGroup):
#     name = State()
#     address = State()
#
#
# @dp.message_handler(commands=['reg'])
# async def user_register(message: types.Message):
#     await message.answer("Введите своё имя")
#     await UserState.name.set()
#
#
# @dp.message_handler(state=UserState.name)
# async def get_username(message: types.Message, state: FSMContext):
#     await state.update_data(username=message.text)
#     await message.answer("Отлично! Теперь введите ваш адрес.")
#     await UserState.next()  # либо же UserState.adress.set()
#
#
#
# @dp.message_handler(state=UserState.address)
# async def get_address(message: types.Message, state: FSMContext):
#     await state.update_data(address=message.text)
#     data = await state.get_data()
#     await message.answer(f"Имя: {data['username']}\n"
#                          f"Адрес: {data['address']}")
#
#     await state.finish()


# @dp.callback_query_handler(Text(startswith=["week_day_empty", "week_day_"]))
# async def callback_empty(call: types.CallbackQuery, state: FSMContext):
#     await call.answer()
#     return
# @dp.callback_query_handler(Text(startswith=["day_"]))
# async def callback_empty(call: types.CallbackQuery, state: FSMContext):
#     await call.answer()
#     return








#
# @dp.message_handler(commands="start")
# async def cmd_start(message: types.Message):
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#     buttons = ["С пюрешкой", "Без пюрешки"]
#     keyboard.add(*buttons)
#     await message.answer("Как подавать котлеты?", reply_markup=keyboard)
# @dp.message_handler(Text(equals="С пюрешкой"))
# async def with_puree(message: types.Message):
#     await message.reply("Отличный выбор!")
#
# @dp.message_handler(lambda message: message.text == "Без пюрешки")
# async def without_puree(message: types.Message):
#     await message.reply("Так невкусно!")
#
# @dp.message_handler(commands="special_buttons")
# async def cmd_special_buttons(message: types.Message):
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     keyboard.add(types.KeyboardButton(text="Запросить геолокацию", request_location=True))
#     keyboard.add(types.KeyboardButton(text="Запросить контакт", request_contact=True))
#     keyboard.add(types.KeyboardButton(text="Создать викторину",
#                                       request_poll=types.KeyboardButtonPollType(type=types.PollType.QUIZ)))
#     await message.answer("Выберите действие:", reply_markup=keyboard)
#
# @dp.message_handler(content_types=['location'])
# async def handle_location(message: types.Message):
#     lat = message.location.latitude
#     lon = message.location.longitude
#     await asyncio.sleep(10)
#     reply = "latitude:  {}\nlongitude: {}".format(lat, lon)
#     await message.answer(reply, reply_markup=types.ReplyKeyboardRemove())
#
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(msg: types.Message):
    await msg.answer(f'Я бот. Приятно познакомиться, {msg.from_user.first_name}')
#
# @dp.message_handler(content_types=['text'])
# async def get_text_messages(msg: types.Message):
#    if msg.text.lower() == 'привет':
#        await msg.answer('Привет!')
#    else:
#        await msg.answer('Не понимаю, что это значит.')
#
