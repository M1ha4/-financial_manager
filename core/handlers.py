from telebot import types
from core import user_manager

# В памяти
user_data = {}  # {user_id: {name, age, balance, expenses: {категория: сумма}}}

# Категории расходов
CATEGORIES = ["Еда", "Квартира", "Развлечения", "Транспорт", "Инвестиции", "Другое"]


def register_handlers(bot, all_users, data_file):
    """Регистрация всех обработчиков"""

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        user_id = message.from_user.id
        user_data[user_id] = {
            "name": "",
            "age": "",
            "balance": "",
            "expenses": {}
        }

        bot.send_message(message.chat.id, "Привет! Как тебя зовут?")
        bot.register_next_step_handler(message, get_name)

    def get_name(message):
        user_id = message.from_user.id
        user_data[user_id]["name"] = message.text.strip()

        bot.send_message(message.chat.id, f"Приятно познакомиться, {message.text}! А сколько тебе лет?")
        bot.register_next_step_handler(message, get_age)

    def get_age(message):
        user_id = message.from_user.id

        if not message.text.isdigit():
            msg = bot.reply_to(message, 'Пожалуйста, введите возраст цифрами. Сколько тебе лет?')
            bot.register_next_step_handler(msg, get_age)
            return

        user_data[user_id]["age"] = message.text

        bot.send_message(message.chat.id, "Отлично! Теперь введи, сколько у тебя сейчас денег (в рублях).")
        bot.register_next_step_handler(message, get_balance)

    def get_balance(message):
        user_id = message.from_user.id

        if not message.text.isdigit():
            msg = bot.reply_to(message, 'Пожалуйста, введи сумму цифрами. Сколько у тебя сейчас денег?')
            bot.register_next_step_handler(msg, get_balance)
            return

        balance = int(message.text)

        if balance <= 0:
            msg = bot.reply_to(message, 'Баланс должен быть больше нуля. Введи корректную сумму.')
            bot.register_next_step_handler(msg, get_balance)
            return

        user_data[user_id]["balance"] = str(balance)

        # Сохраняем пользователя в список в памяти (пока без расходов)
        all_users.append([user_data[user_id]["name"], user_data[user_id]["age"], str(balance)])

        # Сохраняем пользователя в файл
        user_manager.save_user_to_file(
            data_file,
            user_data[user_id]["name"],
            user_data[user_id]["age"],
            str(balance)
        )

        # Переходим к расходам
        bot.send_message(
            message.chat.id,
            "✅ Регистрация завершена.\n\n"
            f"Имя: {user_data[user_id]['name']}\n"
            f"Возраст: {user_data[user_id]['age']}\n"
            f"Баланс: {balance} руб.\n"
            f"Всего пользователей: {len(all_users)}\n\n"
            "Теперь соберём информацию о твоих расходах.\n"
            "У нас 6 категорий: Еда, Квартира, Развлечения, Транспорт, Инвестиции, Другое."
        )
        bot.send_message(message.chat.id, f"💰 Сколько вы тратите на {CATEGORIES[0]} в месяц?")
        bot.register_next_step_handler(message, get_expense, 0)

    def get_expense(message, index):
        user_id = message.from_user.id

        if not message.text.isdigit():
            msg = bot.reply_to(
                message,
                f"Введите сумму цифрами. Сколько вы тратите на {CATEGORIES[index]}?"
            )
            bot.register_next_step_handler(msg, get_expense, index)
            return

        amount = int(message.text)
        user_data[user_id]["expenses"][CATEGORIES[index]] = amount

        # Если есть ещё категории — спрашиваем следующую
        if index + 1 < len(CATEGORIES):
            bot.send_message(message.chat.id, f"Сколько вы тратите на {CATEGORIES[index + 1]} в месяц?")
            bot.register_next_step_handler(message, get_expense, index + 1)
        else:
            # Все категории заполнены — показываем итог
            summary = "📊 Ваши расходы:\n"
            total_expenses = 0
            for cat, val in user_data[user_id]["expenses"].items():
                summary += f"- {cat}: {val} руб.\n"
                total_expenses += val

            balance = int(user_data[user_id]["balance"])

            summary += f"\n💸 Общие расходы: {total_expenses} руб."

            bot.send_message(
                message.chat.id,
                "✅ Сбор данных завершён!\n\n"
                f"Имя: {user_data[user_id]['name']}\n"
                f"Возраст: {user_data[user_id]['age']}\n"
                f"Баланс: {balance} руб.\n\n"
                f"{summary}"
            )
