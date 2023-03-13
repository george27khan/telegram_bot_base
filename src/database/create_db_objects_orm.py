import os
from dotenv import load_dotenv
import json
from src.database.postgres_db import engine, Session
from sqlalchemy import (
    create_engine,
    insert,
    MetaData,
    Table,
    String,
    Time,
    JSON,
    Integer,
    Numeric,
    Column,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

# from sqlalchemy.ext.declarative import declarative_base
# SET timezone="UTC";
# SET TIME ZONE 'posix/Asia/Almaty';
# SHOW timezone;

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = Column(Integer(), primary_key=True)
    telegram = Column(String(1000), nullable=False, comment="username из telegram")
    phone = Column(String(20), nullable=False, comment="Номер из telegram")
    user_name = Column(String(1000), nullable=False, comment="Имя из telegram")
    created_dt = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_on = Column(
        DateTime(),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )
    __table_args__ = (Index("idx_pk_user", "id"),)
    employees = relationship("Scheduler", backref="user")


class Scheduler(Base):
    __tablename__ = "scheduler"
    id = Column(Integer(), primary_key=True)
    id_user = Column(Integer(), ForeignKey("user.id"), nullable=False)
    id_employee = Column(Integer(), ForeignKey("employee.id"), nullable=False)
    start_dt = Column(
        DateTime(), nullable=False, comment="Дата и время начала бронирования"
    )
    end_dt = Column(
        DateTime(), nullable=False, comment="Дата и время окончания бронирования"
    )
    created_dt = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_on = Column(
        DateTime(),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )
    __table_args__ = (Index("idx_pk_scheduler", "id"), Index("idx_fk_user", "id"))


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
    updated_on = Column(
        DateTime(),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )
    __table_args__ = (
        Index("idx_pk_employee", "id"),
        Index("idx_fk_position", "id_position"),
    )
    users = relationship("Scheduler", backref="employee")
    position = relationship("Position")


class Position(Base):
    __tablename__ = "position"
    id = Column(Integer(), primary_key=True)
    position_name = Column(String(500), nullable=False)
    created_dt = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_on = Column(
        DateTime(),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )
    __table_args__ = (Index("idx_pk_position", "id"),)
    employees = relationship("Employee")


class Setting(Base):
    __tablename__ = "setting"
    # id = Column(Integer(), primary_key=True)
    setting_code = Column(String(100), primary_key=True)
    setting_describe = Column(String(1000), nullable=False)
    number_value = Column(Numeric())
    string_value = Column(String(1000))
    date_value = Column(DateTime())
    json_value = Column(JSON())
    created_dt = Column(DateTime(), server_default=func.now(), nullable=False)
    updated_on = Column(
        DateTime(),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )
    __table_args__ = (Index("idx_pk_settings", "setting_code"),)


def init_database():
    # #отчистка базы от таблиц
    Base.metadata.drop_all(engine)
    #
    # #создание в базе всех описанных таблицы
    Base.metadata.create_all(engine)

    session_time_hour = Setting(
        setting_code="session_time_hour",
        setting_describe="Продолжительность приема в часах",
        number_value=0.25,
    )
    start_hour = json.dumps(
        {"Mon": 9, "Tue": 9, "Wed": 9, "Thu": 9, "Fri": 9, "Sat": 9, "Sun": 9}
    )
    end_hour = json.dumps(
        {"Mon": 18, "Tue": 18, "Wed": 18, "Thu": 18, "Fri": 18, "Sat": 16, "Sun": 16}
    )
    start_hour_scheduler = Setting(
        setting_code="start_hour_scheduler",
        setting_describe="График начала рабочего дня",
        json_value=start_hour,
    )
    end_hour_scheduler = Setting(
        setting_code="end_hour_scheduler",
        setting_describe="График конца рабочего дня",
        json_value=end_hour,
    )
    with Session() as s:  # открытие сессии транзакции
        # добавление данных
        s.add_all(
            [
                start_hour_scheduler,
                end_hour_scheduler,
                session_time_hour,
            ]
        )
        # print(session.new)
        s.commit()

# init_database()