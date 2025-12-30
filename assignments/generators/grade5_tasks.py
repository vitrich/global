# generators/grade5_tasks.py - Генератор заданий для 5 класса
from random import randint, shuffle, choice
from math import gcd

def lcm(a, b):
    """Вычисляет наименьшее общее кратное"""
    return abs(a * b) // gcd(a, b)

def prime_factors(n):
    """Возвращает список простых делителей числа"""
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors

def generate_gcd_questions(num_questions=4):
    """Генерирует вопросы про НОД для 5 класса"""
    questions = []
    
    for _ in range(num_questions):
        # Генерируем числа через простые множители
        factors_a = [randint(2, 5) for _ in range(randint(1, 3))]
        factors_b = [randint(2, 5) for _ in range(randint(1, 3))]
        
        a = 1
        for f in factors_a:
            a *= f
        b = 1
        for f in factors_b:
            b *= f
        
        # Иногда добавляем общие множители
        if randint(0, 1):
            common = randint(2, 5)
            a *= common
            b *= common
        
        answer = gcd(a, b)
        
        questions.append({
            'type': 'gcd',
            'text': f'Найди НОД({a}, {b})',
            'answer': answer,
            'answer_text': str(answer),
            'a': a,
            'b': b
        })
    
    return questions


def generate_lcm_questions(num_questions=4):
    """Генерирует вопросы про НОК для 5 класса"""
    questions = []
    
    for _ in range(num_questions):
        a = randint(4, 20)
        b = randint(4, 20)
        
        answer = lcm(a, b)
        
        questions.append({
            'type': 'lcm',
            'text': f'Найди НОК({a}, {b})',
            'answer': answer,
            'answer_text': str(answer),
            'a': a,
            'b': b
        })
    
    return questions


def generate_gcd_lcm_combined(num_questions=3):
    """Генерирует вопросы НОД и НОК вместе"""
    questions = []
    
    for _ in range(num_questions):
        a = randint(6, 30)
        b = randint(6, 30)
        
        answer_gcd = gcd(a, b)
        answer_lcm = lcm(a, b)
        
        questions.append({
            'type': 'gcd_lcm_combined',
            'text': f'Найди НОД и НОК для чисел {a} и {b}',
            'answer_gcd': answer_gcd,
            'answer_lcm': answer_lcm,
            'answer_text': f'НОД: {answer_gcd}, НОК: {answer_lcm}',
            'a': a,
            'b': b
        })
    
    return questions


def generate_factorization_questions(num_questions=3):
    """Генерирует вопросы про разложение на простые множители"""
    questions = []
    
    for _ in range(num_questions):
        # Генерируем число через простые множители
        power_2 = randint(0, 4)
        power_3 = randint(0, 3)
        power_5 = randint(0, 2)
        power_7 = randint(0, 2) if randint(0, 1) else 0
        
        number = (2 ** power_2) * (3 ** power_3) * (5 ** power_5) * (7 ** power_7)
        
        # Формируем правильный ответ
        factors = []
        if power_2 > 0:
            factors.extend([2] * power_2)
        if power_3 > 0:
            factors.extend([3] * power_3)
        if power_5 > 0:
            factors.extend([5] * power_5)
        if power_7 > 0:
            factors.extend([7] * power_7)
        
        answer_text = ' × '.join(map(str, factors)) if factors else '1'
        
        questions.append({
            'type': 'factorization',
            'text': f'Разложи число {number} на простые множители',
            'answer': factors,
            'answer_text': answer_text,
            'number': number
        })
    
    return questions


def generate_divisibility_questions(num_questions=3):
    """Генерирует вопросы про делимость и делители"""
    questions = []
    
    for _ in range(num_questions):
        a = randint(3, 8)
        b = randint(2, 6)
        
        # Формируем делимое через произведение множителей
        divs = [2 ** a[0], 3 ** b[0], 5 ** a[1]] if a else []
        dividend = 1
        for d in divs:
            dividend *= d
        
        # Формируем делитель
        divisor = randint(2, 20)
        
        is_divisible = dividend % divisor == 0
        
        questions.append({
            'type': 'divisibility',
            'text': f'Делится ли {dividend} на {divisor}? Если да, найди частное.',
            'answer': dividend // divisor if is_divisible else 'Не делится',
            'answer_text': str(dividend // divisor) if is_divisible else 'Не делится',
            'is_divisible': is_divisible
        })
    
    return questions


def generate_assignment(topic, num_questions=6):
    """Генерирует полное задание для 5 класса
    topic: 'gcd', 'lcm', 'gcd_lcm', 'factorization' или 'mixed'
    """
    if topic == 'gcd':
        questions = generate_gcd_questions(num_questions)
    elif topic == 'lcm':
        questions = generate_lcm_questions(num_questions)
    elif topic == 'gcd_lcm':
        questions = generate_gcd_lcm_combined(num_questions)
    elif topic == 'factorization':
        questions = generate_factorization_questions(num_questions)
    elif topic == 'mixed':
        # Смешанное задание из разных типов
        questions = []
        questions.extend(generate_gcd_questions(2))
        questions.extend(generate_lcm_questions(2))
        questions.extend(generate_factorization_questions(2))
    else:
        raise ValueError("Invalid topic")
    
    shuffle(questions)
    return questions
