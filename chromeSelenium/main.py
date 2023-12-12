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




def find_record(chat_id):
    with open('file.html', 'r') as file:
        src = file.read()

    soup = bs4.BeautifulSoup(src, 'lxml')
    items = soup.find_all('td', class_='wr-month-calendar-table__day-cell wr-month-calendar-table__day-cell--available')

    if len(items) == 0:
        pass

    else:
        time.sleep(3)
        bot.send_message(chat_id, text= f'\nК врачу свободно {len(items)} или больше записей ')

    return


def main(url, chat_id):

    service = Service(
        executable_path='C:\\Users\\alexa\\PycharmProjects\\recordSCRAPER\\chromeSelenium\\chromedriver.exe')
    driver = webdriver.Chrome(service=service)

    driver.get(url=url)
    driver.add_cookie(
        {"name": "WR_SESSION", "value": "32fb05772d6914ad25d07a8878b763030ef7bec42-eHXw47eGZZopNUNFuBGD4q/UBv3P3LOQAcBRpWmKyKsarRixqSuKDf6xrP7qVyHQP7YpphUZWDBiwuqRZA7ZFn41y3gsLGgLi4k0t/PBQvv8Ljyd2+k1a9vXK3VeBm7aJUiun75/jzn5DKufUKA9ytxL8ZZNMe1+C9GHs06YbQVaM6JnPiZip5b7Y1+EGas8sLTfvIHNKZm+E3DMFmBGRdoDtYRI4Ke9jPpRg0SDVEJT9CihSVHkQnBZXv/yLFU7/U7h5ugJ4bMCp4pJdvH9JYtCB5aud7PD8d0r4ojf+LOUt8jWQDkVMRtSBwSlApElD8PlNVlAbmKr4jSNi4R7ktCX1MVhSSlfikxXYU4WfpahhSDsEtpOei8cNYwKr1WqxGxAnU42KWLINPM/Nww7CHzwNWpeh/hMDJqerTUBSIfJaFGvhnV8jYEDERrosxmDHdpLhsXo97r2iZuhHf2Md5E="}
                    )
    time.sleep(5)
    driver.get(url=url)
    time.sleep(10)

    with open('file.html', 'w') as file:
        file.write(driver.page_source)
    find_record(chat_id)
    driver.close()
    driver.quit()

    return

@bot.message_handler(commands=['delete'])
def delete(message):

    cur.execute('DELETE FROM users WHERE user_id = %s', [message.from_user.id])
    bot.send_message(message.chat.id, text='Вы успешно удалили сборщик.')



bot.polling()