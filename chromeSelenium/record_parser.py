import schedule
from selenium import webdriver
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import bs4
import telebot
from envparse import Env
from config import host, db_name, password, user
import psycopg2
import multiprocessing
import os


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


def find_record(chat_id, driver):
    with open('file.html', 'r') as file:
        src = file.read()

    soup = bs4.BeautifulSoup(src, 'lxml')
    items = soup.find_all('td', class_='wr-month-calendar-table__day-cell wr-month-calendar-table__day-cell--available')

    if len(items) == 0:
        pass

    else:
        driver.fullscreen_window()
        time.sleep(3)
        bot.send_message(chat_id, text= f'\nК врачу свободно {len(items)} или больше записей ')
        driver.save_screenshot(f'{chat_id}.png')
        time.sleep(15)
        bot.send_photo(chat_id, photo=open(f'{chat_id}.png', 'rb'))
        os.remove(f'{str(chat_id)}.png')
    return


def main(url, chat_id):

    service = Service(
        executable_path='C:\\Users\\alexa\\PycharmProjects\\recordSCRAPER\\chromeSelenium\\chromedriver.exe'
        )

    driver = webdriver.Chrome(service=service)
    cur.execute('SELECT cookie FROM users')
    cookie = str(cur.fetchone())[2:-3]

    driver.get(url=url)
    driver.add_cookie(
        {"name": "WR_SESSION", "value": f"{cookie}"}
                )
    time.sleep(5)

    driver.get(url=url)
    time.sleep(45)
    with open('file.html', 'w') as file:
        file.write(driver.page_source)

    find_record(chat_id, driver)
    driver.close()
    driver.quit()
    return

def aprnce_record(user):

    cur.execute('SELECT url FROM users WHERE user_id = %s', [user])
    url = ''.join(cur.fetchone())
    main(url, int(str(user)[1:-2]))

def select_users():
    cur.execute('SELECT user_id FROM users')
    users = cur.fetchall()
    return users

def func(pool):

    users = select_users()
    pool.map(aprnce_record, users)


if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=2)
    for i in range(1,10):
        try:
            schedule.every(30).minutes.do(lambda: func(pool))

            while True:
                schedule.run_pending()


        except Exception as ex:
            bot.send_message(857813877, text=f'Ошибка!  \n{ex}')



