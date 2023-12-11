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
        main(message.text, chat_id)
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
        bot.send_message(chat_id, text='Записей нет. ')

    else:
        bot.send_message(chat_id, text= f'\nК врачу свободно {len(items)} или больше записей ')

    return


def main(url, chat_id):

    service = Service(
        executable_path='C:\\Users\\alexa\\PycharmProjects\\recordSCRAPER\\chromeSelenium\\chromedriver.exe')
    driver = webdriver.Chrome(service=service)

    driver.get(url=url)
    driver.add_cookie(
        {"name": "WR_SESSION", "value": "16a163f647bfc9bc2e2d06fe9af3ae0cf79e3de02-+E0jE1wp2YU1myLMtx/Gt2wgcrJCSXBDpBeUMU/mVw9qO/caQwyueNGy143tDMO9FHvK6rqciNJAwfN4mDZBaq0fz3tITRWjXGR/z6SvVEOdJ8v5BbokGOr8e7vS9xzK53ypGYYK9DFfxrG2Db8dNvjKeKYXkeJKutM1HMOBFymVeHqw9BHmlb8RhmEideHBKgUm6EvjIuG1KiA8paSBwMSWoeYzNB6P8I0TELMSAfE2cL2nbC9JdR76hZM4YReCHIfr0Mc+mcHneLEl6iyUTA5hcdoMzv7LTExGXNm9nF3vavT1tmpGDW1Uazb9FkikbjWeQ4of4N5d0XXE8Bgrbh988VxzYliEeHdk/cRFNDBROXu3WgP7NQfgfEJezXwmeFktgg8ypAKgXPspfHQA4byfN2LY7qDxScmaHXTojmUvLtfY79FsMU4k2e/MKPiicp4QIUkqQUtuDWT1Miuxopk="}
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

def aprnce_record():

    cur.execute('SELECT user_id FROM users')
    users = cur.fetchall()

    for user in users:
        cur.execute('SELECT url FROM users WHERE user_id = %s', [user])
        url = ''.join(cur.fetchone())
        main(url, int(str(user)[1:-2]))


aprnce_record()

bot.polling()