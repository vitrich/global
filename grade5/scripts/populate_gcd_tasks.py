import random
import math
from grade5.models import Task

def run():
    """
    Создать 200 задач на нахождение НОД.
    topic_number = 1 (например, тема «НОД»),
    number = 1..200.
    """
    topic_number = 1
    tasks = []

    # на всякий случай не дублируем, а очищаем старые задачи этой темы
    Task.objects.filter(topic_number=topic_number).delete()

    for i in range(1, 201):  # 1..200
        # генерируем два неравных положительных числа
        a = random.randint(10, 999)
        b = random.randint(10, 999)
        while a == b:
            b = random.randint(10, 999)

        gcd_val = math.gcd(a, b)

        text = f"Найдите наибольший общий делитель чисел {a} и {b}."
        task = Task(
            topic_number=topic_number,
            number=i,
            text=text,
            correct_answer=str(gcd_val),
        )
        tasks.append(task)

    Task.objects.bulk_create(tasks)
    print(f"Создано {len(tasks)} задач на НОД для темы {topic_number}.")
