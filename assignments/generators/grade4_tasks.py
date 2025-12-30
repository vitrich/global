# generators/grade4_tasks.py - Генератор заданий для 4 класса
from random import randint, shuffle
from math import gcd

def generate_fraction_questions(num_questions=5):
    """Генерирует вопросы про дроби для 4 класса"""
    questions = []
    
    # Тип 1: Найди число, если его 1/b часть равна c
    for _ in range(num_questions):
        b = randint(3, 11)
        c = randint(2, 10) * b
        answer = c * b
        
        questions.append({
            'type': 'fraction_find_number',
            'text': f'Найди число, если его 1/{b} часть равна {c}',
            'answer': answer,
            'answer_text': str(answer)
        })
    
    # Тип 2: Найди 1/a часть от d
    for _ in range(num_questions):
        a = randint(2, 15)
        d = a * randint(3, 14)
        answer = d // a
        
        questions.append({
            'type': 'fraction_find_part',
            'text': f'Найди 1/{a} часть от {d}',
            'answer': answer,
            'answer_text': str(answer)
        })
    
    # Тип 3: Найди число, если его a/b часть равна c
    for _ in range(num_questions):
        a = randint(2, 10)
        b = a + randint(3, 12)
        c = a * randint(2, 10) * b
        answer = c * b // a
        
        questions.append({
            'type': 'fraction_find_number_complex',
            'text': f'Найди число, если его {a}/{b} часть равна {c}',
            'answer': answer,
            'answer_text': str(answer)
        })
    
    # Тип 4: Найди a/b часть от d
    for _ in range(num_questions):
        a = randint(3, 13)
        b = a + randint(5, 10)
        d = a * b * randint(2, 5)
        answer = d * a // b
        
        questions.append({
            'type': 'fraction_find_part_complex',
            'text': f'Найди {a}/{b} часть от {d}',
            'answer': answer,
            'answer_text': str(answer)
        })
    
    return questions


def generate_percentage_questions(num_questions=5):
    """Генерирует вопросы про проценты для 4 класса"""
    questions = []
    
    # Тип 1: Найди число, если его a% равны c
    for _ in range(num_questions):
        a = randint(5, 50)
        b = randint(3, 20)
        c = a * b * 100
        answer = c * 100 // a
        
        questions.append({
            'type': 'percent_find_number',
            'text': f'Найди число, если его {a}% равны {c}',
            'answer': answer,
            'answer_text': str(answer)
        })
    
    # Тип 2: Найди a% от d
    for _ in range(num_questions):
        a = randint(5, 50)
        b = randint(4, 20)
        d = a * b * 100
        answer = d * a // 100
        
        questions.append({
            'type': 'percent_find_part',
            'text': f'Найди {a}% от {d}',
            'answer': answer,
            'answer_text': str(answer)
        })
    
    return questions


def generate_assignment(topic, num_questions=6):
    """Генерирует полное задание для 4 класса
    topic: 'fractions' или 'percentages'
    """
    if topic == 'fractions':
        questions = generate_fraction_questions(num_questions)
    elif topic == 'percentages':
        questions = generate_percentage_questions(num_questions)
    else:
        raise ValueError("Invalid topic")
    
    shuffle(questions)
    return questions
