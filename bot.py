import telebot
from config import DATA_FILE
from my_token import token
from core import handlers, user_manager

# Инициализация бота
bot = telebot.TeleBot(token)

# Загружаем пользователей из файла
all_users = user_manager.load_users_from_file(DATA_FILE)
print(f"Загружено пользователей из файла: {len(all_users)}")

# Регистрируем обработчики
handlers.register_handlers(bot, all_users, DATA_FILE)

if __name__ == '__main__':
    print("Бот запущен! Данные будут сохраняться в файл:", DATA_FILE)
    bot.infinity_polling()
