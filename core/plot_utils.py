import os
import matplotlib
matplotlib.use('Agg')  # Без GUI
import matplotlib.pyplot as plt

def plot_expenses(user_data, user_id):
    """
    Создаёт круговую диаграмму расходов для пользователя и возвращает путь к файлу.
    :param user_data: словарь с данными всех пользователей
    :param user_id: ID текущего пользователя
    :return: путь к сохранённому изображению
    """
    expenses = user_data[user_id]["expenses"]
    labels = list(expenses.keys())
    values = list(expenses.values())

    plt.figure(figsize=(6,6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title("Примерные месячные расходы")

    # Добавляем суммарные расходы внизу диаграммы
    total = sum(values)
    plt.text(0, -1.2, f"Суммарные расходы: {total} руб.", ha='center', fontsize=12)

    # Создаём папку data, если её нет
    os.makedirs("data/diagrams_rigistration", exist_ok=True)
    img_path = f"data/diagrams_rigistration/expenses_{user_id}.png"
    plt.savefig(img_path, bbox_inches='tight')
    plt.close()
    return img_path
