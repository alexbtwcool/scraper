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

@bot.message_handler(commands=['start'])
def start(message):
    print(type(message.chat.id))
    user_id = message.from_user.id
    bot.reply_to(message, text=f"""Привет, уважаемый пользователь. \n
Для того, чтобы начать попытку забрать свободную запись введите команду - /url""")

@bot.message_handler(commands=['url'])
def url(message):

    cur.execute('SELECT user_id FROM users WHERE user_id = %s', [message.from_user.id])
    if cur.fetchone() is None:
        bot.send_message(message.chat.id, text=f'Чтобы начать парсить отправьте мне ссылку со страницы нужного врача. \nПример той страницы, какая будет корректна:')
        bot.send_photo(message.chat.id, photo=open('пример.png', 'rb'))
        bot.send_message(message.chat.id, text='⚠️ БУДЬТЕ ВНИМАТЕЛЬНЫ! \nСборник записей будет работать неккоректно, если Вы укажете неправильную ссылку!')
        bot.register_next_step_handler(message, next_step)
    else:
        bot.send_message(message.chat.id, text='Вы уже поставили сборник записей. Желаете его удалить? \n/delete')

def next_step(message):

    chat_id = message.chat.id
    user_id = message.from_user.id

    try:
        cur.execute('INSERT INTO users VALUES(%s, %s)', [user_id, message.text])

    except ValueError as ex:
        bot.send_message(chat_id, text='Что-то пошло не так... Убедитесь корректен ли URL-адрес.')
        print(ex)

    return

@bot.message_handler(commands=['cookie'])
def cookie(message):
    if message.from_user.id == 857813877:
        bot.send_message(message.from_user.id, text='Отправьте cookie.')
        bot.register_next_step_handler(message, cookie_next)

def cookie_next(message):
    cur.execute('UPDATE users SET cookie = %s', [message.text])

@bot.message_handler(commands=['delete'])
def delete(message):

    cur.execute('DELETE FROM users WHERE user_id = %s', [message.from_user.id])
    bot.send_message(message.chat.id, text='Вы успешно удалили сборщик.')



bot.polling()

