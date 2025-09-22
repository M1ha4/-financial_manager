from telebot import types
from core import user_manager

# В памяти
user_data = {}  # {user_id: {name, age, balance, income, expenses: {категория: сумма}}}

CATEGORIES = ["Еда", "Квартира", "Развлечения", "Транспорт", "Инвестиции", "Другое"]

def register_handlers(bot, all_users, data_file):

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        user_id = message.from_user.id
        user_data[user_id] = {
            "name": "",
            "age": "",
            "balance": "",
            "income": "",
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
            msg = bot.reply_to(message, 'Пожалуйста, введите возраст цифрами.')
            bot.register_next_step_handler(msg, get_age)
            return

        user_data[user_id]["age"] = message.text
        bot.send_message(message.chat.id, "Сколько вы зарабатываете в месяц (в рублях)?")
        bot.register_next_step_handler(message, get_income)

    def get_income(message):
        user_id = message.from_user.id
        if not message.text.isdigit():
            msg = bot.reply_to(message, 'Введите доход числом.')
            bot.register_next_step_handler(msg, get_income)
            return

        user_data[user_id]["income"] = int(message.text)
        bot.send_message(message.chat.id, "Отлично! Теперь введите, сколько у вас сейчас денег (баланс, в рублях).")
        bot.register_next_step_handler(message, get_balance)

    def get_balance(message):
        user_id = message.from_user.id
        if not message.text.isdigit():
            msg = bot.reply_to(message, 'Пожалуйста, введите сумму цифрами.')
            bot.register_next_step_handler(msg, get_balance)
            return

        balance = int(message.text)
        if balance <= 0:
            msg = bot.reply_to(message, 'Баланс должен быть больше нуля.')
            bot.register_next_step_handler(msg, get_balance)
            return

        user_data[user_id]["balance"] = balance

        # Сохраняем предварительные данные без расходов
        all_users.append([
            user_data[user_id]["name"],
            user_data[user_id]["age"],
            balance,
            user_data[user_id]["income"]
        ])
        user_manager.save_user_to_file(
            data_file,
            user_data[user_id]["name"],
            user_data[user_id]["age"],
            balance,
            user_data[user_id]["income"]
        )

        bot.send_message(
            message.chat.id,
            "✅ Регистрация завершена. Теперь соберём информацию о ваших расходах.\n"
            "Категории: Еда, Квартира, Развлечения, Транспорт, Инвестиции, Другое.\n"
            f"💰 Сколько вы тратите на {CATEGORIES[0]} в месяц?"
        )
        bot.register_next_step_handler(message, get_expense, 0)

    def get_expense(message, index):
        user_id = message.from_user.id
        if not message.text.isdigit():
            msg = bot.reply_to(message, f"Введите сумму цифрами. Сколько вы тратите на {CATEGORIES[index]}?")
            bot.register_next_step_handler(msg, get_expense, index)
            return

        amount = int(message.text)
        user_data[user_id]["expenses"][CATEGORIES[index]] = amount

        if index + 1 < len(CATEGORIES):
            bot.send_message(message.chat.id, f"Сколько вы тратите на {CATEGORIES[index + 1]} в месяц?")
            bot.register_next_step_handler(message, get_expense, index + 1)
        else:
            total_expenses = sum(user_data[user_id]["expenses"].values())
            balance = user_data[user_id]["balance"]
            income = user_data[user_id]["income"]

            summary = "📊 Ваши расходы:\n"
            for cat, val in user_data[user_id]["expenses"].items():
                summary += f"- {cat}: {val} руб.\n"
            summary += f"\n💸 Общие расходы: {total_expenses} руб."
            summary += f"\n💰 Остаток после расходов: {income - total_expenses} руб."

            # Сохраняем все данные с расходами и общей суммой расходов
            user_manager.save_user_to_file(
                data_file,
                user_data[user_id]["name"],
                user_data[user_id]["age"],
                balance,
                income,
                user_data[user_id]["expenses"],
                total_expenses
            )

            bot.send_message(
                message.chat.id,
                "✅ Сбор данных завершён!\n\n"
                f"Имя: {user_data[user_id]['name']}\n"
                f"Возраст: {user_data[user_id]['age']}\n"
                f"Доход: {income} руб.\n"
                f"Баланс: {balance} руб.\n\n"
                f"{summary}"
            )
