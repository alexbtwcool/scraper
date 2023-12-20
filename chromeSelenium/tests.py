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


conn = psycopg2.connect(
    host=host,
    database=db_name,
    user=user,
    password=password
)
cur = conn.cursor()
conn.autocommit = True


service = Service(
        executable_path='C:\\Users\\alexa\\PycharmProjects\\recordSCRAPER\\chromeSelenium\\chromedriver.exe')

driver = webdriver.Chrome(service=service)
driver.get