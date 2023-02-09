import os
from dotenv import load_dotenv

from sqlalchemy import (
    create_engine,
    insert,
    MetaData,
    Table,
    String,
    Integer,
    Numeric,
    Column,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Index
)
from sqlalchemy.sql import func
from sqlalchemy.orm import mapper
from datetime import datetime

"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Устанавливаем соединение с postgres
connection = psycopg2.connect(user="postgres", password="1111")
connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Создаем курсор для выполнения операций с базой данных
cursor = connection.cursor()
sql_create_database = 
# Создаем базу данных
cursor.execute('create database sqlalchemy_tuts')
# Закрываем соединение
cursor.close()
connection.close()
"""
# загрузка переменных окружения
dotenv_path = os.path.join(os.path.dirname(__file__), "../../.env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# Подключение к серверу PostgreSQL на localhost с помощью psycopg2 DBAPI
engine = create_engine(
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    #,echo=True
)
conn = engine.connect()

metadata = MetaData()

user = Table(
    "user",
    metadata,
    Column("id", Integer(), primary_key=True),
    Column("telegram", String(1000), nullable=False, comment="username из telegram"),
    Column("phone", String(20), nullable=False, comment="Номер из telegram"),
    Column("user_name", String(1000), nullable=False, comment="Имя из telegram"),
    Column("created_dt", DateTime(), server_default=func.now(), nullable=False),
    Column("updated_on", DateTime(), server_default=func.now(), server_onupdate=func.now(), nullable=False),
    Index("idx_pk_user", "id"),
)

scheduler = Table(
    "scheduler",
    metadata,
    Column("id", Integer(), primary_key=True),
    Column("id_user", Integer(), ForeignKey(user.c.id), nullable=False),
    Column("visit_dt", DateTime(), nullable=False, comment="Дата и время бронирования"),
    Column("created_dt", DateTime(), server_default=func.now(), nullable=False),
    Column("updated_on", DateTime(), server_default=func.now(), server_onupdate=func.now(), nullable=False),
    Index("idx_pk_scheduler", "id"),
    Index("idx_fk_user", "id_user"),
)
position = Table(
    "position",
    metadata,
    Column("id", Integer(), primary_key=True),
    Column("position_name", String(500), nullable=False),
    Column("created_dt", DateTime(), server_default=func.now(), nullable=False),
    Column("updated_on", DateTime(), server_default=func.now(), server_onupdate=func.now(), nullable=False),
    Index("idx_pk_position", "id"),
)
employee = Table(
    "employee",
    metadata,
    Column("id", Integer(), primary_key=True),
    Column("first_name", String(100), nullable=False),
    Column("middle_name", String(100), nullable=False),
    Column("last_name", String(100), nullable=False),
    Column("birth_date", DateTime(), nullable=False),
    Column("email", String(1000), nullable=False),
    Column("phone_number", String(20), nullable=False),
    Column("id_position", Integer(), ForeignKey(position.c.id), nullable=False),
    Column("is_male", Boolean(), nullable=False, comment="Пол"),
    Column("hire_date", DateTime(), server_default=func.now(), nullable=False),
    Column("created_dt", DateTime(), server_default=func.now(), nullable=False),
    Column("updated_on", DateTime(), server_default=func.now(), server_onupdate=func.now(), nullable=False),
    Index("idx_pk_employee", "id"),
    Index("idx_fk_position", "id_position")
)

setting = Table(
    "setting",
    metadata,
    Column("id", Integer(), primary_key=True),
    Column("setting_code", String(100), nullable=False),
    Column("setting_describe", String(1000), nullable=False),
    Column("number_value", Numeric()),
    Column("string_value", String(1000)),
    Column("date_value", DateTime()),
    Column("created_dt", DateTime(), server_default=func.now(), nullable=False),
    Column("updated_on", DateTime(), server_default=func.now(), server_onupdate=func.now(), nullable=False),
    #Index("idx_pk_settings", "id"),
)


class User(object):
    pass
class Scheduler(object):
    pass
class Position(object):
    pass
class Employee(object):
    pass
class Setting(object):
    pass

mapper(User, user)
mapper(Scheduler, scheduler)
mapper(Position, position)
mapper(Employee, employee)
mapper(Setting, setting)

#отчистка базы от таблиц
metadata.drop_all(engine)

#создание в базе всех описанных таблицы
metadata.create_all(engine)

setting_list = [
    {
        "setting_code": "session_time_hour",
        "setting_describe": "Продолжительность приема в часах",
        "number_value": 0.25
    },
    {
        "setting_code": "monday_start_hour",
        "setting_describe": "Начало рабочего дня в понедельник",
        "number_value": 9
    },
    {
        "setting_code": "tuesday_start_hour",
        "setting_describe": "Начало рабочего дня в вторник",
        "number_value": 9
    },
    {
        "setting_code": "wednesday_start_hour",
        "setting_describe": "Начало рабочего дня в среду",
        "number_value": 9
    },
    {
        "setting_code": "thursday_start_hour",
        "setting_describe": "Начало рабочего дня в четверг",
        "number_value": 9
    },
    {
        "setting_code": "friday_start_hour",
        "setting_describe": "Начало рабочего дня в пятницу",
        "number_value": 9
    },
    {
        "setting_code": "saturday_start_hour",
        "setting_describe": "Начало рабочего дня в субботу",
        "number_value": 10
    },
    {
        "setting_code": "sunday_start_hour",
        "setting_describe": "Начало рабочего дня в воскресенье",
        "number_value": 10
    },
    {
        "setting_code": "monday_end_hour",
        "setting_describe": "Конец рабочего дня в понедельник",
        "number_value": 18
    },
    {
        "setting_code": "tuesday_end_hour",
        "setting_describe": "Конец рабочего дня в вторник",
        "number_value": 18
    },
    {
        "setting_code": "wednesday_end_hour",
        "setting_describe": "Конец рабочего дня в среду",
        "number_value": 18
    },
    {
        "setting_code": "thursday_end_hour",
        "setting_describe": "Конец рабочего дня в четверг",
        "number_value": 18
    },
    {
        "setting_code": "friday_end_hour",
        "setting_describe": "Конец рабочего дня в пятницу",
        "number_value": 18
    },
    {
        "setting_code": "saturday_end_hour",
        "setting_describe": "Конец рабочего дня в субботу",
        "number_value": 16
    },
    {
        "setting_code": "sunday_end_hour",
        "setting_describe": "Конец рабочего дня в воскресенье",
        "number_value": 16
    },
]
t = conn.begin() #start transaction
res = conn.execute(insert(setting), setting_list)
print(res.rowcount)
t.commit()