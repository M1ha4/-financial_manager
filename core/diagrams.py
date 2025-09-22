import matplotlib.pyplot as plt



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
