import os
from dotenv import load_dotenv
import json
from datetime import datetime as dt
from src.database.postgres_db_async import async_engine, async_session
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
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import relationship, DeclarativeBase, mapped_column, Mapped
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram: Mapped[str] = mapped_column(
        type_=String(1000), nullable=False, comment="username из telegram"
    )
    phone: Mapped[str] = mapped_column(
        type_=String(20), nullable=False, comment="Номер из telegram"
    )
    user_name: Mapped[str] = mapped_column(
        type_=String(1000), nullable=False, comment="Имя из telegram"
    )
    created_dt: Mapped[dt] = mapped_column(server_default=func.now(), nullable=False)
    updated_on: Mapped[dt] = mapped_column(
        server_default=func.now(), server_onupdate=func.now(), nullable=False
    )
    __table_args__ = (Index("idx_pk_user", "id"),)
    employees = relationship("Scheduler", backref="user")


class Scheduler(Base):
    __tablename__ = "scheduler"
    id: Mapped[int] = mapped_column(primary_key=True)
    id_user: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    id_employee: Mapped[int] = mapped_column(ForeignKey("employee.id"), nullable=False)
    start_dt: Mapped[dt] = mapped_column(
        nullable=False, comment="Дата и время начала бронирования"
    )
    end_dt: Mapped[dt] = mapped_column(
        nullable=False, comment="Дата и время окончания бронирования"
    )
    created_dt: Mapped[dt] = mapped_column(server_default=func.now(), nullable=False)
    updated_on: Mapped[dt] = mapped_column(
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )
    __table_args__ = (Index("idx_pk_scheduler", "id"), Index("idx_fk_user", "id"))


class Employee(Base):
    __tablename__ = "employee"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[dt] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(String(1000), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    id_position: Mapped[int] = mapped_column(ForeignKey("position.id"), nullable=False)
    is_male: Mapped[Boolean] = mapped_column(nullable=False, comment="Пол")
    hire_date: Mapped[dt] = mapped_column(server_default=func.now(), nullable=False)
    created_dt: Mapped[dt] = mapped_column(server_default=func.now(), nullable=False)
    updated_on: Mapped[dt] = mapped_column(
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
    id: Mapped[int] = Column(primary_key=True)
    position_name: Mapped[str] = mapped_column(String(500), nullable=False)
    created_dt: Mapped[dt] = mapped_column(server_default=func.now(), nullable=False)
    updated_on: Mapped[dt] = mapped_column(
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )
    __table_args__ = (Index("idx_pk_position", "id"),)
    employees = relationship("Employee")


class Setting(Base):
    __tablename__ = "setting"
    # id = Column(Integer(), primary_key=True)
    setting_code: Mapped[str] = mapped_column(String(100), primary_key=True)
    setting_describe: Mapped[str] = mapped_column(String(1000), nullable=False)
    number_value: Mapped[int]
    string_value: Mapped[str] = mapped_column(String(1000))
    date_value: Mapped[dt]
    json_value: Mapped[str] = mapped_column(JSON())
    created_dt: Mapped[dt] = mapped_column(server_default=func.now(), nullable=False)
    updated_on: Mapped[dt] = mapped_column(
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )
    __table_args__ = (Index("idx_pk_settings", "setting_code"),)


async def init_position(async_session: async_sessionmaker[AsyncSession]) -> None:
    async with async_session() as sess:
        async with sess.begin():
            p1 = Position(position_name="Младший специалист")
            p2 = Position(position_name="Специалист")
            p3 = Position(position_name="Ведущий специалист")
            p4 = Position(position_name="Старший специалист")
            p5 = Position(position_name="Главный специалист")
            sess.add_all([p1, p2, p3, p4, p5])
            # sess.commit()
async def init_setting(async_session: async_sessionmaker[AsyncSession]) -> None:
    async with async_session() as sess:
        async with sess.begin():
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
            sess.add_all(
                [
                    start_hour_scheduler,
                    end_hour_scheduler,
                    session_time_hour,
                ]
            )
            # sess.commit()


async def init_database(async_session: async_sessionmaker[AsyncSession]) -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) #отчистка базы от таблиц
        await conn.run_sync(Base.metadata.create_all) #создание в базе всех описанных таблицы

    await init_setting(async_session)
    await init_position(async_session)

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await async_engine.dispose()


init_database(async_session)
