import os
from telebot import types
from core import user_manager
from core.plot_utils import plot_expenses

# Убедимся, что папка data существует
os.makedirs("data", exist_ok=True)

# В памяти
user_data = {}  # {user_id: {name, age, balance, income, expenses: {категория: сумма}, goals: []}}

CATEGORIES = ["Еда", "Квартира", "Развлечения", "Транспорт", "Инвестиции", "Другое"]

GOALS = {
    "goal_save": "Накопить",
    "goal_optimize": "Оптимизировать траты",
    "goal_advice": "Получать советы от Финансового помощника",
    "goal_other": "Другое"
}


def register_handlers(bot, all_users, data_file):

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        user_id = message.from_user.id
        user_data[user_id] = {
            "name": "",
            "age": "",
            "balance": "",
            "income": "",
            "expenses": {},
            "goals": []
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
        if balance < 0:
            msg = bot.reply_to(message, 'Баланс должен быть не меньше нуля.')
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
            img_path = plot_expenses(user_data, user_id)
            bot.send_photo(
                message.chat.id,
                photo=open(img_path, 'rb'),
                caption=(
                    "✅ Сбор данных завершён!\n\n"
                    f"Имя: {user_data[user_id]['name']}\n"
                    f"Возраст: {user_data[user_id]['age']}\n"
                    f"Доход: {user_data[user_id]['income']} руб.\n"
                    f"Баланс: {user_data[user_id]['balance']} руб.\n"
                    f"Суммарные расходы: {sum(user_data[user_id]['expenses'].values())} руб."
                )
            )

            # После расходов → спрашиваем цели
            ask_goals(message)

    def ask_goals(message):
        user_id = message.from_user.id
        user_data[user_id]["goals"] = []

        markup = types.InlineKeyboardMarkup(row_width=1)
        for key, val in GOALS.items():
            markup.add(types.InlineKeyboardButton(val, callback_data=key))
        markup.add(types.InlineKeyboardButton("✅ Готово", callback_data="goal_done"))

        bot.send_message(
            message.chat.id,
            "🎯 Теперь выберите основные цели использования бота (можно несколько):",
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("goal_"))
    def callback_goals(call):
        user_id = call.from_user.id
        goals = user_data[user_id].get("goals", [])

        if call.data == "goal_done":
            user_manager.save_user_to_file(
                data_file,
                user_data[user_id]["name"],
                user_data[user_id]["age"],
                user_data[user_id]["balance"],
                user_data[user_id]["income"],
                user_data[user_id]["expenses"],
                sum(user_data[user_id]["expenses"].values()),
                goals
            )
            bot.edit_message_text(
                f"🎯 Ваши цели сохранены: {', '.join(goals) if goals else 'не выбрано'}",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
            return

        goal = GOALS[call.data]
        if goal in goals:
            goals.remove(goal)
        else:
            goals.append(goal)

        user_data[user_id]["goals"] = goals

        # Перерисовываем кнопки с галочками
        markup = types.InlineKeyboardMarkup(row_width=1)
        for key, val in GOALS.items():
            text = f"✅ {val}" if val in goals else val
            markup.add(types.InlineKeyboardButton(text, callback_data=key))
        markup.add(types.InlineKeyboardButton("✅ Готово", callback_data="goal_done"))

        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
