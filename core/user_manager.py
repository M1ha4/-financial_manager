import os

def load_users_from_file(file_path: str):
    """Загрузка пользователей из файла"""
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            pass
        return []

    users = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(',')
                    # Если есть расходы, их тоже загружаем
                    if len(parts) >= 3:
                        name = parts[0]
                        age = parts[1]
                        balance = parts[2]
                        expenses = {}
                        if len(parts) > 3:
                            # Расходы: категория:сумма
                            for exp in parts[3:]:
                                cat, val = exp.split(':')
                                expenses[cat] = int(val)
                        users.append([name, age, balance, expenses])
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")

    return users


def save_user_to_file(file_path: str, name: str, age: str, balance: str, expenses: dict = None):
    """Сохранение пользователя в файл"""
    try:
        with open(file_path, 'a', encoding='utf-8') as f:
            line = f"{name},{age},{balance}"
            if expenses:
                for cat, val in expenses.items():
                    line += f",{cat}:{val}"
            line += "\n"
            f.write(line)
    except Exception as e:
        print(f"Ошибка при записи в файл: {e}")
