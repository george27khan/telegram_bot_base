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

from src.database import engine, Session, Setting, Scheduler, User


from sqlalchemy import exc as sql_exc
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

g_hour_start_d = {"Mon": 9, "Tue": 9, "Wed": 9, "Thu": 9, "Fri": 9, "Sat": 9, "Sun": 9}
g_hour_end_d = {
    "Mon": 18,
    "Tue": 18,
    "Wed": 18,
    "Thu": 18,
    "Fri": 18,
    "Sat": 18,
    "Sun": 18,
}
g_session_time = 0.25
logging.basicConfig(level=logging.INFO)
g_datetime_format = "%d.%m.%Y %H:%M:%S"
g_date_format = "%d.%m.%Y"
g_time_format = "%H:%M"


def load_settings():
    global g_hour_start_d, g_hour_end_d, g_session_time
    with Session() as session:
        g_hour_start_d = json.loads(
            session.get(Setting, "start_hour_scheduler").json_value
        )
        g_hour_end_d = json.loads(session.get(Setting, "end_hour_scheduler").json_value)
        g_session_time = session.get(Setting, "session_time_hour").number_value


load_settings()


def get_time_format(hour: float) -> str:
    return f"{int(hour // 1)}:{int(hour % 1 * 60):02}"


dotenv_path = os.path.join(os.path.dirname(__file__), "../../.env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TELEGRAMM_BOT_TOKEN = os.getenv("TELEGRAMM_BOT_TOKEN")
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
    start_time = chosen_date.replace(
        hour=int(start_hour), minute=int((start_hour % 1) * 60)
    )
    end_time = chosen_date.replace(hour=int(end_hour), minute=int((end_hour % 1) * 60))
    while start_time < end_time:
        next_time = start_time + dt.timedelta(
            hours=int(g_session_time), minutes=int((g_session_time % 1) * 60)
        )
        button_text = (
            f"{start_time.strftime(g_time_format)}-{next_time.strftime(g_time_format)}"
        )
        buttons.append(
            types.InlineKeyboardButton(
                text=button_text,
                callback_data=f"{start_time.strftime(g_datetime_format)},{next_time.strftime(g_datetime_format)}",
            )
        )
        start_time = next_time
    buttons.append(
        types.InlineKeyboardButton(
            text="?????????????????? ?? ???????????? ??????", callback_data=f"current_month"))
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    keyboard.add(*buttons)
    return keyboard


def get_calendar_keyboard(base_date: dt.date) -> types.InlineKeyboardMarkup:
    lang = "en"
    max_calendar_month = 2
    current_month = dt.date.today().month
    days_in_month = calendar.monthrange(base_date.year, base_date.month)[1]
    first_month_date = base_date.replace(day=1)
    dates_of_month = [
        first_month_date + dt.timedelta(day) for day in range(days_in_month)
    ]
    map_day_to_name_ru = {1: "????", 2: "????", 3: "????", 4: "????", 5: "????", 6: "????", 7: "????"}
    map_day_to_name_en = {
        1: "Mon",
        2: "Tue",
        3: "Wed",
        4: "Thu",
        5: "Fri",
        6: "Sat",
        7: "Sun",
    }
    week_ru = {
        "Mon": "????",
        "Tue": "????",
        "Wed": "????",
        "Thu": "????",
        "Fri": "????",
        "Sat": "????",
        "Sun": "????",
    }

    days_of_week = list(g_hour_start_d.keys())
    cur_month_name = base_date.strftime("%B")
    cur_day = base_date.day

    # ?????????? ??????????????????
    buttons = [
        types.InlineKeyboardButton(text=day_name, callback_data=f"week_day")
        for day, day_name in enumerate(days_of_week)
    ]

    # ???????????????????????? ?????????????????? ?? ????????????
    for empty in range(0, first_month_date.weekday()):
        buttons.append(types.InlineKeyboardButton(text=" ", callback_data=f"empty_day"))

    for day, date in enumerate(dates_of_month):
        if date < dt.date.today():
            buttons.append(
                types.InlineKeyboardButton(
                    text=str(day + 1), callback_data=f"empty_day"
                )
            )
        else:
            buttons.append(
                types.InlineKeyboardButton(
                    text=str(day + 1),
                    callback_data=f"day_{date.strftime(g_date_format)}",
                )
            )

    # ???????????????????????? ?????????????????? ?? ??????????
    last_week_len = len(buttons) % 7
    if 0 < last_week_len < 7:
        for empty in range(0, 7 - last_week_len):
            buttons.append(
                types.InlineKeyboardButton(text=" ", callback_data=f"empty_day")
            )
    if base_date.month > current_month:
        buttons.append(
            types.InlineKeyboardButton(
                text="???????????????????? ??????????", callback_data=f"prev_month"
            )
        )
    if base_date.month < current_month + max_calendar_month:
        buttons.append(
            types.InlineKeyboardButton(
                text="?????????????????? ??????????", callback_data=f"next_month"
            )
        )
    keyboard = types.InlineKeyboardMarkup(row_width=7)
    keyboard.add(*buttons)
    return keyboard

@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ["???????????????? ??????????"]
    keyboard.add(*buttons)
    await message.answer("???????????????? ????????????????:", reply_markup=keyboard)

@dp.callback_query_handler(Text(startswith=["next_month"]), state=Booking.choose_day)
async def make_calendar_next(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    next_date = state_data["state_current_date"] + relativedelta(months=1)
    await call.message.answer(
        "???????????????? ???????? ????????????????????????:", reply_markup=get_calendar_keyboard(next_date)
    )
    await state.update_data(state_current_date=next_date)
    await call.answer()


@dp.callback_query_handler(Text(startswith=["prev_month"]), state=Booking.choose_day)
async def make_calendar_prev(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    prev_date = state_data["state_current_date"] - relativedelta(months=1)
    await call.message.answer(
        "???????????????? ???????? ????????????????????????:", reply_markup=get_calendar_keyboard(prev_date)
    )
    await state.update_data(state_current_date=prev_date)
    await call.answer()

@dp.message_handler(Text(startswith=["current_month"]), state=Booking.choose_day)
async def make_calendar(message: types.Message, state: FSMContext):
    await message.answer(
        "???????????????? ???????? ????????????????????????:",
        reply_markup=get_calendar_keyboard(dt.date.today()),
    )
    await state.update_data(state_current_date=dt.date.today())
    await Booking.choose_day.set()  # ???????????? ?? ?????????????????? ???????????? ??????


@dp.message_handler(Text(equals="???????????????? ??????????"))
async def make_calendar(message: types.Message, state: FSMContext):
    await message.answer(
        "???????????????? ???????? ????????????????????????:",
        reply_markup=get_calendar_keyboard(dt.date.today()),
    )
    await state.update_data(state_current_date=dt.date.today())
    await Booking.choose_day.set()  # ???????????? ?? ?????????????????? ???????????? ??????


# @dp.callback_query_handler(Text(startswith=["empty_day"]), state=Booking.choose_day)
# async def callback_empty(call: types.CallbackQuery):
#     await call.answer()


@dp.callback_query_handler(state=Booking.choose_day)
async def callback_choose_day(call: types.CallbackQuery):
    if call.data in ("empty_day", "week_day"):
        await call.answer()
        return
    button_datetime = dt.datetime.strptime(call.data[4:], g_date_format)
    await Booking.choose_time.set()  # ???????????? ?? ?????????????????? ???????????? ??????
    await call.message.answer(
        "???????????????? ?????????? ????????????????????????:",
        reply_markup=get_time_keyboard(button_datetime),
    )

@dp.callback_query_handler(state=Booking.choose_time)
async def callback_choose_time(call: types.CallbackQuery, state: FSMContext):
    start_datetime, end_datetime = [
        dt.datetime.strptime(dt_str, g_datetime_format)
        for dt_str in call.data.split(",")
    ]
    user_obj = User(
        id=call.message.chat.id,
        telegram=call.message.chat.username,
        phone="",
        user_name=f"{call.message.chat.first_name} {call.message.chat.last_name}",
    )
    scheduler_obj = Scheduler(
        id_user=call.message.chat.id,
        id_employee=1,
        start_dt=start_datetime,
        end_dt=end_datetime,
    )
    with Session() as s:
        try:
            s.add(user_obj)
            s.commit()
        except sql_exc.IntegrityError:
             s.rollback()
        s.add(scheduler_obj)
        s.commit()
    await call.answer(text=f"?????????????????? ???????????????????????? ???? {start_datetime.strftime(g_date_format)} c "
                           f"{start_datetime.strftime(g_time_format)} ???? {end_datetime.strftime(g_time_format)}",
                      show_alert=True)
    await state.finish()

#
# class UserState(StatesGroup):
#     name = State()
#     address = State()
#
#
# @dp.message_handler(commands=['reg'])
# async def user_register(message: types.Message):
#     await message.answer("?????????????? ???????? ??????")
#     await UserState.name.set()
#
#
# @dp.message_handler(state=UserState.name)
# async def get_username(message: types.Message, state: FSMContext):
#     await state.update_data(username=message.text)
#     await message.answer("??????????????! ???????????? ?????????????? ?????? ??????????.")
#     await UserState.next()  # ???????? ???? UserState.adress.set()
#
#
#
# @dp.message_handler(state=UserState.address)
# async def get_address(message: types.Message, state: FSMContext):
#     await state.update_data(address=message.text)
#     data = await state.get_data()
#     await message.answer(f"??????: {data['username']}\n"
#                          f"??????????: {data['address']}")
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
#     buttons = ["?? ????????????????", "?????? ??????????????"]
#     keyboard.add(*buttons)
#     await message.answer("?????? ???????????????? ???????????????", reply_markup=keyboard)
# @dp.message_handler(Text(equals="?? ????????????????"))
# async def with_puree(message: types.Message):
#     await message.reply("???????????????? ??????????!")
#
# @dp.message_handler(lambda message: message.text == "?????? ??????????????")
# async def without_puree(message: types.Message):
#     await message.reply("?????? ????????????????!")
#
# @dp.message_handler(commands="special_buttons")
# async def cmd_special_buttons(message: types.Message):
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     keyboard.add(types.KeyboardButton(text="?????????????????? ????????????????????", request_location=True))
#     keyboard.add(types.KeyboardButton(text="?????????????????? ??????????????", request_contact=True))
#     keyboard.add(types.KeyboardButton(text="?????????????? ??????????????????",
#                                       request_poll=types.KeyboardButtonPollType(type=types.PollType.QUIZ)))
#     await message.answer("???????????????? ????????????????:", reply_markup=keyboard)
#
# @dp.message_handler(content_types=['location'])
# async def handle_location(message: types.Message):
#     lat = message.location.latitude
#     lon = message.location.longitude
#     await asyncio.sleep(10)
#     reply = "latitude:  {}\nlongitude: {}".format(lat, lon)
#     await message.answer(reply, reply_markup=types.ReplyKeyboardRemove())
#
@dp.message_handler(commands=["start", "help"])
async def send_welcome(msg: types.Message):
    await msg.answer(f"?? ??????. ?????????????? ??????????????????????????, {msg.from_user.first_name}")


#
# @dp.message_handler(content_types=['text'])
# async def get_text_messages(msg: types.Message):
#    if msg.text.lower() == '????????????':
#        await msg.answer('????????????!')
#    else:
#        await msg.answer('???? ??????????????, ?????? ?????? ????????????.')
#
