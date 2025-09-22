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
                    if len(parts) == 3:  # имя, возраст, баланс
                        name, age, balance = parts
                        users.append([name, age, balance])
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")

    return users


def save_user_to_file(file_path: str, name: str, age: str, balance: str):
    """Сохранение пользователя в файл"""
    try:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(f"{name},{age},{balance}\n")
    except Exception as e:
        print(f"Ошибка при записи в файл: {e}")
