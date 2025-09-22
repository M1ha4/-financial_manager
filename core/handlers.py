from telebot import types
from core import user_manager

# В памяти
user_data = {}  # {user_id: [name, age]}

def register_handlers(bot, all_users, data_file):
    """Регистрация всех обработчиков"""

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
        user_manager.save_user_to_file(data_file, name, age)

        bot.send_message(message.chat.id, f"Спасибо! Твои данные сохранены.\n"
                                          f"Имя: {name}\n"
                                          f"Возраст: {age}\n"
                                          f"Всего пользователей: {len(all_users)}")
