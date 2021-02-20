from telebot import types


keyboard_start = types.ReplyKeyboardMarkup(True)
keyboard_start.row('Что делать?', 'Лайк', 'Гороскоп фо тудэй')


keyboard_zodiac = types.InlineKeyboardMarkup()
zodiacs = ['Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева', 'Весы',
           'Скорпион', 'Стрелец', 'Козерог', 'Водолей', 'Рыбы']
for zodiac in zodiacs:
    key_someone = types.InlineKeyboardButton(text=zodiac, callback_data='zodiac')
    keyboard_zodiac.add(key_someone)

