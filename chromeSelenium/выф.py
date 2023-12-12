import schedule
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
        {"name": "WR_SESSION", "value": "693b70f4b1113439fcf056a57bc7cf87512314712-t6ZlHyLy4Gx2TxvkStb4+k3+kuMMW3alDNBFSfqBxsZqAZgcm0Zh9+1Kkf5qVK6uOUZPwdPNAVZuq1xn48XnID8tbl17TNxv1Qe882tNSR3i6otk28BkCPLTYkB3S6/rc4RzcJ8wr6N0jRVQ9+Vroy60WQPdq6IliWbcB1givhvq9ckDUGFfWonHZgJEDNr5IezSiymVlWoP87/SPqfnijYFyQwQKRcWD0m0+UGzb9zMZIVUuC2R474pmsVzB3BCWRmNoXwpGWEJfYnCGmy3f7xoMHrontlzaxj8erGEIB8nAeQMuud1bRzXFVV2ii6WozbRXHl6K32PIH2K6wjThPf/yD0Gy92A6zo/7wgcRSUby+vaKneiizzPUFwa4mr+V34ceGflCtGcGBlwCcLEvmmDFKrpZ2K3dwc21ci01tEOKgJb/9snBf88YwBHDQGQUT9HWsU7E10sIOUDz94yDPU="}
                    )
    time.sleep(5)
    driver.get(url=url)
    time.sleep(45)

    with open('file.html', 'w') as file:
        file.write(driver.page_source)
    find_record(chat_id)
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
    schedule.every(1).minutes.do(lambda: func(pool))

    while True:
        schedule.run_pending()
