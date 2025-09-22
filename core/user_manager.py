import os

def save_user_to_file(file_path, name, age, balance, income=None, expenses=None, total_expenses=None, goals=None):
    """Сохраняет пользователя в файл"""
    try:
        with open(file_path, 'a', encoding='utf-8') as f:
            parts = [str(name), str(age), str(balance)]
            if income is not None:
                parts.append(str(income))
            if expenses:
                for cat, val in expenses.items():
                    parts.append(f"{cat}:{val}")
            if total_expenses is not None:
                parts.append(f"total_expenses:{total_expenses}")
            if goals:
                goals_str = "|".join(goals)  # сохраняем список через |
                parts.append(f"goals:{goals_str}")
            line = ",".join(parts) + "\n"
            f.write(line)
    except Exception as e:
        print(f"Ошибка при записи в файл: {e}")


def load_users_from_file(file_path):
    """Загрузка всех пользователей из файла"""
    if not os.path.exists(file_path):
        return []

    users = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(',')
                # первые 3 обязательные поля
                name, age, balance = parts[0:3]
                income = int(parts[3]) if len(parts) >= 4 and parts[3].isdigit() else None
                expenses = {}
                total_expenses = None
                goals = []
                if len(parts) > 4:
                    for p in parts[4:]:
                        if p.startswith("total_expenses:"):
                            total_expenses = int(p.split(":")[1])
                        elif p.startswith("goals:"):
                            goals = p.split(":")[1].split("|")
                        else:
                            cat, val = p.split(":")
                            expenses[cat] = int(val)
                users.append({
                    "name": name,
                    "age": age,
                    "balance": int(balance),
                    "income": income,
                    "expenses": expenses,
                    "total_expenses": total_expenses,
                    "goals": goals
                })
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")

    return users
