import os
from telebot import types
from core import user_manager
import matplotlib
matplotlib.use('Agg')  # Используем бэкенд для файлов, без GUI
import matplotlib.pyplot as plt

# Убедимся, что папка data существует
os.makedirs("data", exist_ok=True)
#from core.diagrams import plot_expenses


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

            # Генерация круговой диаграммы
            img_path = plot_expenses(user_id)

            # Отправка диаграммы пользователю
            bot.send_photo(
                message.chat.id,
                photo=open(img_path, 'rb'),
                caption=(
                    "✅ Сбор данных завершён!\n\n"
                    f"Имя: {user_data[user_id]['name']}\n"
                    f"Возраст: {user_data[user_id]['age']}\n"
                    f"Доход: {income} руб.\n"
                    f"Баланс: {balance} руб.\n"
                    f"Суммарные расходы: {total_expenses} руб."
                )
            )


def plot_expenses(user_id):
    """Создаёт круговую диаграмму расходов и возвращает путь к файлу"""
    expenses = user_data[user_id]["expenses"]
    labels = list(expenses.keys())
    values = list(expenses.values())

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title("Примерные месячные расходы")

    # Добавляем суммарные расходы внизу диаграммы
    total = sum(values)
    plt.text(0, -1.2, f"Суммарные расходы: {total} руб.", ha='center', fontsize=12)

    # Сохраняем изображение
    file_path = f"data/expenses_{user_id}.png"
    plt.savefig(file_path, bbox_inches='tight')
    plt.close()
    return file_path
