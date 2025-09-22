import telebot
from telebot import types
import os
from my_token import token



bot = telebot.TeleBot(token)


user_data = {}  # {user_id: [name, age]}
all_users = []  # [ [name1, age1], [name2, age2], ... ]
DATA_FILE = "Users.txt"  # Имя нашего файла с данными


# Функция для загрузки данных из файла при запуске бота
def load_users_from_file():
    # Проверяем, существует ли файл
    if not os.path.exists(DATA_FILE):
        # Если файла нет, создаем пустой
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            pass  # Просто создаем пустой файл
        return []

    users = []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()  # Убираем лишние пробелы и переносы
                if line:  # Если строка не пустая
                    parts = line.split(',')  # Разделяем строку по запятой
                    # Проверяем, что в строке ровно две части (имя и возраст)
                    if len(parts) == 2:
                        name, age = parts
                        users.append([name, age])
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")

    return users


# Функция для добавления одного пользователя в файл
def save_user_to_file(name, age):
    try:
        # Открываем файл в режиме добавления ('a') с кодировкой UTF-8
        with open(DATA_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{name},{age}\n")  # Записываем данные в формате "имя,возраст"
    except Exception as e:
        print(f"Ошибка при записи в файл: {e}")


# Загружаем существующих пользователей при запуске
all_users = load_users_from_file()
print(f"Загружено пользователей из файла: {len(all_users)}")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_data[user_id] = ['', '']  # [name, age]

    bot.send_message(message.chat.id, "Привет! Как тебя зовут?")
    bot.register_next_step_handler(message, get_name)


def get_name(message):
    user_id = message.from_user.id
    user_data[user_id][0] = message.text

    bot.send_message(message.chat.id, f"Приятно познакомиться, {message.text}! А сколько тебе лет?")
    bot.register_next_step_handler(message, get_age)


def get_age(message):
    user_id = message.from_user.id

    if not message.text.isdigit():
        msg = bot.reply_to(message, 'Пожалуйста, введите возраст цифрами. Сколько тебе лет?')
        bot.register_next_step_handler(msg, get_age)
        return

    age = message.text
    name = user_data[user_id][0]

    # Сохраняем пользователя в список в памяти
    all_users.append([name, age])

    # Сохраняем пользователя в файл
    save_user_to_file(name, age)

    bot.send_message(message.chat.id, f"Спасибо! Твои данные сохранены.\n"
                                      f"Имя: {name}\n"
                                      f"Возраст: {age}\n"
                                      f"Всего пользователей: {len(all_users)}")


if __name__ == '__main__':
    print("Бот запущен! Данные будут сохраняться в файл:", DATA_FILE)
    bot.infinity_polling()