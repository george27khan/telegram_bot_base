import os
from dotenv import load_dotenv

from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    String,
    Integer,
    Column,
    Text,
    DateTime,
    Boolean,
    ForeignKey
)
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
engine.connect()
print(engine)

metadata = MetaData()

user = Table(
    "user",
    metadata,
    Column("id", Integer(), primary_key=True),
    Column("telegram", String(1000), nullable=False, comment="username из telegram"),
    Column("phone", String(1000), nullable=False, comment="Номер из telegram"),
    Column("user_name", String(1000), nullable=False, comment="Имя из telegram"),
    Column("created_dt", DateTime(), default=datetime.now, nullable=False),
    Column("updated_on", DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False)
)

scheduler = Table(
    "scheduler",
    metadata,
    Column("id", Integer(), primary_key=True),
    Column("id_user", Integer(), ForeignKey(user.c.id), nullable=False),
    Column("visit_dt", DateTime(), nullable=False, comment="Дата и время бронирования"),
    Column("created_dt", DateTime(), default=datetime.now, nullable=False),
    Column("updated_on", DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False)
)
#создание в базе всех описанных таблицы
metadata.create_all(engine)