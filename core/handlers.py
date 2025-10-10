import os
from telebot import types
from core import user_manager
from core.plot_utils import plot_expenses

os.makedirs("data", exist_ok=True)

# Хранилище данных в памяти
user_data = {}

CATEGORIES = ["Еда", "Квартира", "Развлечения", "Транспорт", "Инвестиции", "Другое"]
GOALS = {
    "goal_save": "Накопить",
    "goal_optimize": "Оптимизировать траты",
    "goal_advice": "Получать советы",
    "goal_other": "Другое"
}


def register_handlers(bot, all_users, data_file):

    # === /start ===
    @bot.message_handler(commands=['start'])
    def start(message):
        user_id = message.from_user.id
        user_data[user_id] = {
            "name": "",
            "age": "",
            "balance": 0,
            "income": 0,
            "expenses": {},
            "goals": [],
            "target_sum": None,
            "target_months": None,
            "state": "get_name",
            "expense_index": 0
        }
        bot.send_message(message.chat.id, "Привет! Как тебя зовут?")

    # === Обработка текста ===
    @bot.message_handler(func=lambda m: True)
    def handle_text(message):
        user_id = message.from_user.id
        if user_id not in user_data:
            bot.send_message(message.chat.id, "Сначала напишите /start")
            return

        state = user_data[user_id].get("state")

        if state == "get_name":
            get_name(message)
        elif state == "get_age":
            get_age(message)
        elif state == "get_income":
            get_income(message)
        elif state == "get_balance":
            get_balance(message)
        elif state == "get_expense":
            get_expense(message, user_data[user_id]["expense_index"])
        elif state == "await_target_sum":
            get_target_sum(message)
        elif state == "await_target_months":
            get_target_months(message)
        elif state in ["add_income", "add_expense"]:
            handle_income_expense(message)
        else:
            # Основное меню
            if message.text in ["➕ Доход", "➖ Расход", "📊 Статистика", "💸 Долги"]:
                handle_main_menu(message)
            else:
                bot.send_message(message.chat.id, "Выберите действие с помощью кнопок меню 👇")

    # === Регистрация данных ===
    def get_name(message):
        user_id = message.from_user.id
        user_data[user_id]["name"] = message.text.strip()
        user_data[user_id]["state"] = "get_age"
        bot.send_message(message.chat.id, "Сколько тебе лет?")

    def get_age(message):
        user_id = message.from_user.id
        if not message.text.isdigit():
            bot.send_message(message.chat.id, "Введите возраст числом")
            return
        user_data[user_id]["age"] = int(message.text)
        user_data[user_id]["state"] = "get_income"
        bot.send_message(message.chat.id, "Какой у тебя доход в месяц (руб)?")

    def get_income(message):
        user_id = message.from_user.id
        if not message.text.isdigit():
            bot.send_message(message.chat.id, "Введите доход числом")
            return
        user_data[user_id]["income"] = int(message.text)
        user_data[user_id]["state"] = "get_balance"
        bot.send_message(message.chat.id, "Сколько у тебя сейчас денег (баланс)?")

    def get_balance(message):
        user_id = message.from_user.id
        if not message.text.isdigit():
            bot.send_message(message.chat.id, "Введите сумму числом")
            return
        user_data[user_id]["balance"] = int(message.text)
        user_data[user_id]["state"] = "get_expense"
        bot.send_message(message.chat.id, f"Сколько тратите на {CATEGORIES[0]}?")

    def get_expense(message, index):
        user_id = message.from_user.id
        if not message.text.isdigit():
            bot.send_message(message.chat.id, f"Введите сумму числом для {CATEGORIES[index]}")
            return

        amount = int(message.text)
        user_data[user_id]["expenses"][CATEGORIES[index]] = amount

        if index + 1 < len(CATEGORIES):
            user_data[user_id]["expense_index"] = index + 1
            bot.send_message(message.chat.id, f"Сколько тратите на {CATEGORIES[index + 1]}?")
        else:
            # Сумма всех расходов
            total_expenses = sum(user_data[user_id]["expenses"].values())

            # Сохраняем данные в файл
            user_manager.save_user_to_file(
                data_file,
                user_data[user_id]["name"],
                user_data[user_id]["age"],
                user_data[user_id]["balance"],
                user_data[user_id]["income"],
                user_data[user_id]["expenses"],
                total_expenses
            )

            # Строим диаграмму расходов
            img_path = plot_expenses(user_data, user_id)
            bot.send_photo(
                message.chat.id,
                photo=open(img_path, 'rb'),
                caption=(f"✅ Сбор данных завершён!\n\n"
                         f"Имя: {user_data[user_id]['name']}\n"
                         f"Возраст: {user_data[user_id]['age']}\n"
                         f"Доход: {user_data[user_id]['income']} руб.\n"
                         f"Баланс: {user_data[user_id]['balance']} руб.\n"
                         f"Расходы всего: {total_expenses} руб.")
            )

            # Переход к выбору целей
            ask_goals(message)

    # === Цели ===
    def ask_goals(message):
        user_id = message.from_user.id
        markup = types.InlineKeyboardMarkup(row_width=1)
        for key, val in GOALS.items():
            markup.add(types.InlineKeyboardButton(val, callback_data=key))
        markup.add(types.InlineKeyboardButton("✅ Готово", callback_data="goal_done"))
        bot.send_message(message.chat.id, "Выберите цели:", reply_markup=markup)
        user_data[user_id]["state"] = "choose_goals"

    @bot.callback_query_handler(func=lambda call: call.data.startswith("goal_"))
    def callback_goals(call):
        user_id = call.from_user.id
        goals = user_data[user_id].get("goals", [])

        if call.data == "goal_done":
            if "Накопить" in goals and not user_data[user_id].get("target_sum"):
                user_data[user_id]["state"] = "await_target_sum"
                bot.send_message(call.message.chat.id, "💰 Какую сумму хотите накопить?")
                return

            # Сохраняем цели и показываем меню
            user_data[user_id]["state"] = None
            show_main_menu(bot, call.message.chat.id, user_id)
            return

        goal = GOALS[call.data]
        if goal in goals:
            goals.remove(goal)
        else:
            goals.append(goal)
        user_data[user_id]["goals"] = goals

        markup = types.InlineKeyboardMarkup(row_width=1)
        for key, val in GOALS.items():
            text = f"✅ {val}" if val in goals else val
            markup.add(types.InlineKeyboardButton(text, callback_data=key))
        markup.add(types.InlineKeyboardButton("✅ Готово", callback_data="goal_done"))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)

    def get_target_sum(message):
        user_id = message.from_user.id
        if not message.text.isdigit():
            bot.send_message(message.chat.id, "Введите число")
            return
        user_data[user_id]["target_sum"] = int(message.text)
        user_data[user_id]["state"] = "await_target_months"
        bot.send_message(message.chat.id, "За сколько месяцев хотите накопить?")

    def get_target_months(message):
        user_id = message.from_user.id
        if not message.text.isdigit() or int(message.text) <= 0:
            bot.send_message(message.chat.id, "Введите положительное число")
            return
        user_data[user_id]["target_months"] = int(message.text)
        user_data[user_id]["state"] = None
        show_main_menu(bot, message.chat.id, user_id)

    # === Главное меню ===
    def handle_main_menu(message):
        user_id = message.from_user.id
        text = message.text
        if text == "➕ Доход":
            user_data[user_id]["state"] = "add_income"
            bot.send_message(message.chat.id, "Введите сумму дохода:")
        elif text == "➖ Расход":
            user_data[user_id]["state"] = "add_expense"
            bot.send_message(message.chat.id, "Введите сумму расхода:")
        elif text == "📊 Статистика":
            bot.send_message(message.chat.id, "📊 Статистика (пока в разработке)")
        elif text == "💸 Долги":
            bot.send_message(message.chat.id, "💸 Долги (пока в разработке)")

    def handle_income_expense(message):
        user_id = message.from_user.id
        state = user_data[user_id]["state"]
        if not message.text.isdigit():
            bot.send_message(message.chat.id, "Введите сумму числом")
            return
        amount = int(message.text)
        if state == "add_income":
            user_data[user_id]["balance"] += amount
            bot.send_message(message.chat.id, f"✅ Доход +{amount} руб. добавлен")
        else:
            user_data[user_id]["balance"] -= amount
            bot.send_message(message.chat.id, f"✅ Расход -{amount} руб. добавлен")
        user_data[user_id]["state"] = None
        show_main_menu(bot, message.chat.id, user_id)


def show_main_menu(bot, chat_id, user_id):
    balance = user_data[user_id].get("balance", 0)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Доход", "➖ Расход")
    markup.add("📊 Статистика", "💸 Долги")
    bot.send_message(chat_id, f"💰 Баланс: {balance} руб.", reply_markup=markup)
