import logging
import time
import datetime

import telebot
from telebot import types
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
from telebot.types import ReplyKeyboardRemove, CallbackQuery

import pandas as pd
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import configparser

config = configparser.ConfigParser()
config.read('token.ini')
API_TOKEN = config['DEFAULT']['token']
print(API_TOKEN)
Base = declarative_base()
logger = telebot.logger

class User(Base):
    __tablename__ = 'info'

    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String)
    dttm = sql.Column(sql.String)
    workplace = sql.Column(sql.String)

    def __repr__(self):
        return "<User(id='%s', name='%s', dttm='%s', workplace='%s')>" %\
               (self.id, self.name, self.dttm, self.workplace)

    def as_dict(self):
        return {c.id: getattr(self, c.id) for c in self.__table__.columns}


class PostgresConfiguration:

    DB_USER = "postgres"
    DB_PASSWORD = "postgres"
    DB_HOST = "db"
    DB_PORT = "5432"
    DB_NAME = "postgres"

    @property
    def postgres_db_path(self):
        return f'postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'


pg = PostgresConfiguration()
engine = sql.create_engine(pg.postgres_db_path)
Session = sessionmaker(bind=engine)
session = Session()


# Создаем экземпляр бота
bot = telebot.TeleBot(API_TOKEN)

# Creates a unique calendar
calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")


@bot.message_handler(commands=["start"])
def start(message, res=False):

    username = message.from_user.first_name

    bot.send_message(message.chat.id, f'Привет, {username}')

    # Две кнопки
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Занятые места")
    item2 = types.KeyboardButton("Забронировать место")
    markup.add(item1)
    markup.add(item2)

    bot.send_message(message.chat.id, 'Выбери:', reply_markup=markup)


# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    now = datetime.datetime.now()  # Get the current date

    if message.text.strip() == 'Занятые места':
        df = pd.read_sql('SELECT * FROM info', engine)
        df = df[df['dttm'] >= str(datetime.date.today().strftime("%d.%m.%Y"))]
        # bot.send_message(message.chat.id, f"Количество занятых мест: {df.shape[0]}")

        df = df.sort_values(by=['dttm'])
        for index, row in df.iterrows():
           bot.send_message(message.chat.id, f"{row['name']}, {row['dttm']}, {row['workplace']}")

    elif message.text.strip() == 'Забронировать место':
        bot.send_message(
            message.chat.id,
            "Выберите день",
            reply_markup=calendar.create_calendar(
                name=calendar_1_callback.prefix,
                year=now.year,
                month=now.month,
            ),
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1_callback.prefix))
def callback_inline(call: CallbackQuery):

    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    if action == "DAY":
        bot.send_message(
            chat_id=call.from_user.id,
            text=f"Забронировано: {date.strftime('%d.%m.%Y')}",
            reply_markup=ReplyKeyboardRemove(),
        )
        print(f"{calendar_1_callback}: Day: {date.strftime('%d.%m.%Y')}")

        dtypes = {
            "id": "int64",
            "name": "string",
            "dttm": "string",
            "workplace": "string"
        }
        data = pd.DataFrame({
            'id': [round(time.time())],
            'name': [str(call.message.chat.first_name)],
            'dttm': [str(date.strftime('%d.%m.%Y'))],
            'workplace': ["1"]
        }).astype(dtypes)

        data.to_sql('info', engine, index=False, if_exists='append')

    elif action == "CANCEL":
        bot.send_message(
            chat_id=call.from_user.id,
            text="Назад",
            reply_markup=ReplyKeyboardRemove(),
        )
        print(f"{calendar_1_callback}: Cancellation")

# Запускаем бота
bot.polling(none_stop=True, interval=0)