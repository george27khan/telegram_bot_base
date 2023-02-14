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
from sqlalchemy.ext.declarative import declarative_base


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

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(Integer(), primary_key=True)
    telegram = Column(String(1000), nullable=False, comment="username из telegram")
    phone = Column(String(20), nullable=False, comment="Номер из telegram")
    user_name = Column(String(1000), nullable=False, comment="Имя из telegram")
    created_dt = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_on = Column(DateTime(), server_default=func.now(), server_onupdate=func.now(), nullable=False)
    __table_args__ = (
        Index('idx_pk_user', 'id'),
    )

class Scheduler(Base):
    __tablename__ = "scheduler"
    id = Column(Integer(), primary_key=True)
    id_user = Column(Integer(), ForeignKey("user.id"), nullable=False)
    visit_dt = Column(DateTime(), nullable=False, comment="Дата и время бронирования")
    created_dt = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_on = Column(DateTime(), server_default=func.now(), server_onupdate=func.now(), nullable=False)
    __table_args__ = (
        Index('idx_pk_scheduler', 'id'),
        Index('idx_fk_user', 'id')
    )

class Position(Base):
    __tablename__ = "position"
    id = Column(Integer(), primary_key=True)
    position_name = Column(String(500), nullable=False)
    created_dt = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_on = Column(DateTime(), server_default=func.now(), server_onupdate=func.now(), nullable=False)
    __table_args__ = (
        Index('idx_pk_position', 'id'),
    )

class Employee(Base):
    __tablename__ = "employee"
    id = Column(Integer(), primary_key=True)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    birth_date = Column(DateTime(), nullable=False)
    email = Column(String(1000), nullable=False)
    phone_number = Column(String(20), nullable=False)
    id_position = Column(Integer(), ForeignKey("position.id"), nullable=False)
    is_male = Column(Boolean(), nullable=False, comment="Пол")
    hire_date = Column(DateTime(), server_default=func.now(), nullable=False)
    created_dt = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_on = Column(DateTime(), server_default=func.now(), server_onupdate=func.now(), nullable=False)
    __table_args__ = (
        Index("idx_pk_employee", "id"),
        Index("idx_fk_position", "id_position")
    )

class Setting(Base):
    __tablename__ = "setting"
    id = Column(Integer(), primary_key=True)
    setting_code = Column(String(100), nullable=False)
    setting_describe = Column(String(1000), nullable=False)
    number_value = Column(Numeric())
    string_value = Column(String(1000))
    date_value = Column(DateTime())
    created_dt = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_on = Column(DateTime(), server_default=func.now(), server_onupdate=func.now(), nullable=False)
    __table_args__ = (
        Index("idx_pk_settings", "id"),
    )

# #отчистка базы от таблиц
Base.metadata.drop_all(engine)
#
# #создание в базе всех описанных таблицы
Base.metadata.create_all(engine)

'''setting_list = [
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
t.commit()'''