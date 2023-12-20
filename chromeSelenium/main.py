from selenium import webdriver
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import bs4
import telebot
from telebot import types
from telebot.types import Message
from envparse import Env
from config import host, db_name, password, user
import psycopg2
import validators
import multiprocessing
import requests


env = Env()
TOKEN = env.str('TOKEN')
bot = telebot.TeleBot(token=TOKEN, parse_mode='MARKDOWN')

conn = psycopg2.connect(
    host=host,
    database=db_name,
    user=user,
    password=password
)
cur = conn.cursor()
conn.autocommit = True

dentist_fk = 1
orthopedist_fk = 2
cardiologist_fk = 3


@bot.message_handler(commands=['start'])
def start(message):
    print(type(message.chat.id))
    user_id = message.from_user.id
    bot.reply_to(message, text=f"""Здравствуй, уважаемый пользователь. 🌼 \n
Для того, чтобы начать попытку забрать свободную запись введите команду — /collecting""")


@bot.message_handler(commands=['collecting'])
def collecting(message):

    cur.execute('SELECT user_id FROM users WHERE user_id = %s', [message.from_user.id])
    if cur.fetchone() is None:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        dentist = types.KeyboardButton("🦷 Стоматолог (детский)")
        orthopedist = types.KeyboardButton('🤕 Травматолог/ортопед')
        cardiologist = types.KeyboardButton('💓 Кардиолог')
        markup.add(dentist, orthopedist, cardiologist)
        bot.send_message(message.chat.id, text=f'''Теперь выберите в меню интересующего Вас врача 🌱''', reply_markup=markup)
        bot.register_next_step_handler(message, next_step, dentist, orthopedist, cardiologist)
    else:
        bot.send_message(message.chat.id, text='🗑️ Вы уже поставили сборник записей. Желаете его удалить? — /delete')


def next_step(message, dentist, orthopedist, cardiologist):

    chat_id = message.chat.id
    user_id = message.from_user.id

    if message.text == dentist.text:
        cur.execute('INSERT INTO users (user_id, fk_doctor_url) VALUES (%s, %s)', [user_id, dentist_fk])
        bot.send_message(user_id, text=f'Планировщик установлен на врача:\n\n{dentist.text}')

    elif message.text == orthopedist.text:
        cur.execute('INSERT INTO users (user_id, fk_doctor_url) VALUES (%s, %s)', [user_id, orthopedist_fk])
        bot.send_message(user_id, text=f'Планировщик установлен на врача:\n\n{orthopedist.text}')

    elif message.text == cardiologist.text:
        cur.execute('INSERT INTO users (user_id, fk_doctor_url) VALUES (%s, %s)', [user_id, cardiologist_fk])
        bot.send_message(user_id, text=f'Планировщик установлен на врача:\n\n{cardiologist.text}')

    else:
        bot.send_message(user_id, text='⚠️ Используйте меню с кнопками!')
        bot.send_photo(user_id, photo=open('markup.png', 'rb'))

    bot.send_message(chat_id, text='~~ Бот начал сбор информации ~~')

    return


@bot.message_handler(commands=['cookie'])
def cookie(message):
    if message.from_user.id == 857813877:
        bot.send_message(message.from_user.id, text='Отправьте cookie.')
        bot.register_next_step_handler(message, cookie_next)


def cookie_next(message):
    cur.execute('UPDATE users SET cookie = %s WHERE user_id = 857813877', [message.text])
    bot.send_message(message.from_user.id, text='Успешно.')


@bot.message_handler(commands=['delete'])
def delete(message):

    cur.execute('DELETE FROM users WHERE user_id = %s', [message.from_user.id])
    bot.send_message(message.chat.id, text='''Вы успешно удалили сборщик.
Желаете поставить новый сборщик? — /collecting''')


while True:
    try:
        bot.polling()

    except Exception as ex:
        requests.get(f'https://api.telegram.org/bot6631477583:AAFlasFHHf6dMmFMhZPiUbk4p47exasYbf4'
                     f'/sendMessage?chat_id=857813877&text={ex}')
