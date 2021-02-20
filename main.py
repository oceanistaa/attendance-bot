from __future__ import print_function

import telebot
from google.oauth2.service_account import Credentials
import gspread
import random
from datetime import datetime
from threading import Lock
from keyboards import keyboard_start, keyboard_zodiac
import horoscope


f = open('tokens')
BOT_TOKEN = f.readline()[:-1]
SPREADSHEET_ID = f.readline()
f.close()


SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

print('Connecting to spreadsheet...')

cr = Credentials.from_service_account_file('service_account.json', scopes=SCOPES)
gc = gspread.authorize(cr)
sheet = gc.open_by_key(SPREADSHEET_ID).sheet1

print('Connected')

STUDENTS = sheet.col_values(2)[3:-1]
for i in range(len(STUDENTS)):
    STUDENTS[i] = STUDENTS[i].strip()
STUDENTS_BY_ID = {}
print(STUDENTS)

DATES = sheet.row_values(2)[2:]
for i in range(len(DATES)):
    DATES[i] = DATES[i].strip()[4:]

ADMIN_ID = 296322182

random.seed(datetime.now())


def get_today_column():
    m = datetime.today().month
    d = datetime.today().day
    for i in range(len(DATES)):
        date = DATES[i]
        if int(date[:2]) == d and int(date[-2:]) == m:
            return i + 3
    return len(DATES) + 6


def fill_column_zero(col):
    column_name = chr(65 + col - 1)
    fill_range = column_name + str(4) + ':' + column_name + str(len(STUDENTS) + 3)
    sheet.update(fill_range, [[0] for _ in STUDENTS])


def insert_by_name_in_sheet(name):
    index = find_student(name)
    col = get_today_column()
    sheet.update_cell(index + 4, col, 1)


# returns index in list STUDENTS, -1 if there is no such student
def find_student(name):
    for i in range(len(STUDENTS)):
        if STUDENTS[i] == name:
            return i
    return -1


bot = telebot.AsyncTeleBot(BOT_TOKEN)

I_LOVE_YOU_STICKER_ID = 'CAACAgIAAxkBAAIBuGAvepReSBj9IztyihvVzPEcxpJIAALEEgAC6NbiEl2mhsfr7stGHgQ'
SHRUG_STICKER_ID = 'CAACAgIAAxkBAAICbWAv0CRJebkuH6YB776rQM-PWI0eAAI3DQACqAgvCOayUvHh4jAkHgQ'

current_code_lock = Lock()
current_code = 1398742052
last_code_time = datetime.now()

MAX_TIME_DELTA = 20


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет!', reply_markup=keyboard_start)


@bot.message_handler(commands=['registration'])
def start_rega(message):
    chat_id = message.chat.id
    if chat_id in STUDENTS_BY_ID:
        bot.send_message(chat_id, 'Если ты собрался записать еще кого-то, то ты подорвал мое доверие')
        return
    words = message.text.strip().split()
    if len(words) < 2:
        bot.send_message(chat_id, 'Неверное использование. \nЧтобы зарегистрироваться, используй: /registration <ФИО>')
        return
    name = " ".join(words[1:])
    student_index = find_student(name)
    if student_index == -1:
        bot.send_message(message.chat.id, 'Такой студент дазонт экзист, соре, трай эгэйн')
        return
    else:
        bot.send_message(message.chat.id, 'Студент дэтэктид, запиши себя: /mark <код> ')
    chat_id = message.chat.id
    STUDENTS_BY_ID[chat_id] = name


@bot.message_handler(commands=['mark'])
def mark_student(message):
    chat_id = message.chat.id
    words = message.text.strip().split()
    if len(words) != 2 or not words[1].isdigit():
        bot.send_message(chat_id, 'Неверное использование. \nЧтобы записать себя, используй: /mark <код>')
        return
    if chat_id not in STUDENTS_BY_ID:
        bot.send_message(chat_id, 'Ты не зарегистрирован(а)')
        return
    code = int(words[1])
    with current_code_lock:
        minutes_delta = (datetime.now() - last_code_time).seconds / 60
        if minutes_delta > MAX_TIME_DELTA:
            bot.send_message(chat_id, 'Время код истекло')
            return
        if current_code != code:
            bot.send_message(chat_id, 'Неверный код!')
            return
    insert_by_name_in_sheet(STUDENTS_BY_ID[chat_id])
    bot.send_message(chat_id, STUDENTS_BY_ID[chat_id] + ' отмечен(а) ')


@bot.message_handler(commands=['startClass'])
def start_class(message):
    chat_id = message.chat.id
    if chat_id not in STUDENTS_BY_ID:
        bot.send_message(chat_id, 'Ты не зарегистрирован(а)')
        return
    if ADMIN_ID != chat_id:
        bot.send_message(chat_id, 'Нет доступа')
        return

    with current_code_lock:
        global current_code
        global last_code_time
        current_code = random.randint(100000, 999999)
        last_code_time = datetime.now()
        fill_column_zero(get_today_column())
        insert_by_name_in_sheet(STUDENTS_BY_ID[chat_id])
        bot.send_message(chat_id, 'Бот активирован, ты отмечена. Код: ' + str(current_code))


@bot.message_handler(commands=['shrug'])
def shrug_message(message):
    bot.send_sticker(message.chat.id, SHRUG_STICKER_ID)


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'что делать?':
        bot.send_message(message.chat.id, 'Чтобы начать, используй  /registration <ФИО>\n'
                                          'Если ты зареган, чтобы записать себя, используй:  /mark <код>')
        return
    elif message.text.lower() == 'лайк':
        bot.send_sticker(message.chat.id, I_LOVE_YOU_STICKER_ID)
        return
    elif message.text.lower() == 'я люблю тебя':
        bot.send_message(message.chat.id, 'И я тебя, babe')
        return
    elif message.text.lower() == 'гороскоп фо тудэй':
        bot.send_message(message.chat.id, text='Выбери свой знак зодиака', reply_markup=keyboard_zodiac)
        return
    bot.send_message(message.chat.id, 'Странные ты, однако, фразы глаголишь')


# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    # Если нажали на одну из 12 кнопок — выводим гороскоп
    if call.data == "zodiac":
        # Формируем гороскоп
        msg = random.choice(horoscope.first) + ' ' + \
              random.choice(horoscope.second) + ' ' + \
              random.choice(horoscope.second_add) + ' ' + \
              random.choice(horoscope.third)
        # Отправляем текст в Телеграм
        bot.send_message(call.message.chat.id, msg)


print('Telegram bot started')

bot.polling(none_stop=True)
