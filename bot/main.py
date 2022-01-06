import logging
import datetime

import telebot
from telebot import types
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
from telebot.types import ReplyKeyboardRemove, CallbackQuery

API_TOKEN = "5017249833:AAED1JhVzHOFOU4a6sR2_jXQR0MmNOQOjmY"
logger = telebot.logger

# Создаем экземпляр бота
bot = telebot.TeleBot(API_TOKEN)

# Creates a unique calendar
calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")


@bot.message_handler(commands=["start"])
def start(message, res=False):
    bot.send_message(message.chat.id, 'Я на связи. Напиши мне что-нибудь )')

    # Две кнопки
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Свободные места")
    item2 = types.KeyboardButton("Забронировать место")
    markup.add(item1)
    markup.add(item2)

    bot.send_message(message.chat.id, 'Выбери:', reply_markup=markup)


# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    now = datetime.datetime.now()  # Get the current date

    if message.text.strip() == 'Свободные места':
            bot.send_message(message.chat.id, '1')

    elif message.text.strip() == 'Забронировать место':
        bot.send_message(
            message.chat.id,
            "Selected date",
            reply_markup=calendar.create_calendar(
                name=calendar_1_callback.prefix,
                year=now.year,
                month=now.month,  # Specify the NAME of your calendar
            ),
        )

@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1_callback.prefix))
def callback_inline(call: CallbackQuery):

    # At this point, we are sure that this calendar is ours. So we cut the line by the separator of our calendar
    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    # Processing the calendar. Get either the date or None if the buttons are of a different type
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    # There are additional steps. Let's say if the date DAY is selected, you can execute your code. I sent a message.
    if action == "DAY":
        bot.send_message(
            chat_id=call.from_user.id,
            text=f"You have chosen {date.strftime('%d.%m.%Y')}",
            reply_markup=ReplyKeyboardRemove(),
        )
        print(f"{calendar_1_callback}: Day: {date.strftime('%d.%m.%Y')}")
    elif action == "CANCEL":
        bot.send_message(
            chat_id=call.from_user.id,
            text="Cancellation",
            reply_markup=ReplyKeyboardRemove(),
        )
        print(f"{calendar_1_callback}: Cancellation")

# Запускаем бота
bot.polling(none_stop=True, interval=0)