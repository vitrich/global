# views.py - Основные представления для системы проверки знаний
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

from .generators import grade4_tasks
from .models import (
    Assignment, AssignmentVariant, StudentAnswer, 
    SchoolClass, UserProfile, AssignmentTopic, AssignmentStats, StudentStats
)

# Импортируем генераторы
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / 'generators'))

import generators.grade4_tasks
import generators.grade5_tasks# views.py - Основные представления для системы проверки знаний
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import (
    Assignment, AssignmentVariant, StudentAnswer,
    SchoolClass, UserProfile, AssignmentTopic, AssignmentStats, StudentStats
)

# Импортируем генераторы
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / 'generators'))

import generators.grade4_tasks
import grade5_tasks
# assignments/views.py - Основные представления
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import (
    Assignment, AssignmentVariant, StudentAnswer,
    SchoolClass, UserProfile, AssignmentTopic
)


def is_teacher(user):
    """Проверяет, является ли пользователь учителем"""
    if not hasattr(user, 'profile'):
        return False
    return user.profile.role == 'teacher'


def is_student(user):
    """Проверяет, является ли пользователь учеником"""
    if not hasattr(user, 'profile'):
        return False
    return user.profile.role == 'student'


# ===== УЧИТЕЛЬ: УПРАВЛЕНИЕ РАБОТАМИ =====

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    """Панель управления учителя"""
    user = request.user
    classes = user.classes_teaching.all()

    assignments = Assignment.objects.filter(
        school_class__in=classes
    ).order_by('-created_at')

    context = {
        'classes': classes,
        'assignments': assignments,
        'user': user,
    }
    return render(request, 'teacher/dashboard.html', context)


@login_required
@user_passes_test(is_teacher)
def create_assignment(request, class_id):
    """Создание новой проверочной работы"""
    school_class = get_object_or_404(SchoolClass, id=class_id)

    if school_class.teacher != request.user:
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        topic_id = request.POST.get('topic')
        title = request.POST.get('title', '')

        topic = get_object_or_404(AssignmentTopic, id=topic_id, grade=school_class.grade)

        assignment = Assignment.objects.create(
            school_class=school_class,
            topic=topic,
            title=title or f'Работа по теме: {topic.name}',
            created_by=request.user
        )

        generate_variants_for_assignment(assignment)

        return redirect('assignment_detail', assignment_id=assignment.id)

    topics = AssignmentTopic.objects.filter(grade=school_class.grade)
    context = {
        'school_class': school_class,
        'topics': topics,
    }
    return render(request, 'teacher/create_assignment.html', context)


def generate_variants_for_assignment(assignment):
    """Генерирует варианты заданий для всех учеников класса"""
    try:
        from assignments.generators import grade4_tasks, grade5_tasks
    except ImportError:
        # Если генераторы не найдены, создаем пустые варианты
        students = assignment.school_class.students.all()
        for idx, student_profile in enumerate(students, 1):
            AssignmentVariant.objects.create(
                assignment=assignment,
                student=student_profile.user,
                variant_number=idx,
                questions=[]
            )
        return

    students = assignment.school_class.students.all()
    grade = assignment.school_class.grade.grade
    topic_name = assignment.topic.name

    for idx, student_profile in enumerate(students, 1):
        student = student_profile.user

        # Выбираем генератор
        if grade == '4':
            if 'Дроб' in topic_name or 'дроб' in topic_name:
                questions = grade4_tasks.generate_assignment('fractions', num_questions=6)
            elif 'Процент' in topic_name or 'процент' in topic_name:
                questions = grade4_tasks.generate_assignment('percentages', num_questions=6)
            else:
                questions = grade4_tasks.generate_assignment('fractions', num_questions=6)
        elif grade == '5':
            if 'НОД' in topic_name:
                questions = grade5_tasks.generate_assignment('gcd', num_questions=4)
            elif 'НОК' in topic_name:
                questions = grade5_tasks.generate_assignment('lcm', num_questions=4)
            elif 'множител' in topic_name.lower():
                questions = grade5_tasks.generate_assignment('factorization', num_questions=3)
            else:
                questions = grade5_tasks.generate_assignment('mixed', num_questions=6)
        else:
            questions = []

        AssignmentVariant.objects.create(
            assignment=assignment,
            student=student,
            variant_number=idx,
            questions=questions
        )


@login_required
@user_passes_test(is_teacher)
def assignment_detail(request, assignment_id):
    """Просмотр деталей работы и статистики по классу"""
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if assignment.school_class.teacher != request.user:
        return redirect('teacher_dashboard')

    variants = assignment.variants.all().select_related('student')

    stats = {
        'total_students': variants.count(),
        'submitted': 0,
        'total_correct': 0,
        'average_score': 0.0,
    }

    variant_data = []
    for variant in variants:
        answers = variant.answers.all()
        correct = answers.filter(is_correct=True).count()
        total = answers.count()

        percent = (correct / total * 100) if total > 0 else 0

        if answers.exists():
            stats['submitted'] += 1
            stats['total_correct'] += correct

        variant_data.append({
            'variant': variant,
            'student_name': variant.student.get_full_name(),
            'correct': correct,
            'total': total,
            'percent': percent,
        })

    context = {
        'assignment': assignment,
        'variant_data': variant_data,
        'stats': stats,
    }
    return render(request, 'teacher/assignment_detail.html', context)


@login_required
@user_passes_test(is_teacher)
def regenerate_assignment_variants(request, assignment_id):
    """Перегенерирует варианты работы"""
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if assignment.school_class.teacher != request.user:
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        AssignmentVariant.objects.filter(assignment=assignment).delete()
        generate_variants_for_assignment(assignment)
        return redirect('assignment_detail', assignment_id=assignment.id)

    context = {'assignment': assignment}
    return render(request, 'teacher/confirm_regenerate.html', context)


@login_required
@user_passes_test(is_teacher)
def class_statistics(request, class_id):
    """Статистика по классу"""
    school_class = get_object_or_404(SchoolClass, id=class_id)

    if school_class.teacher != request.user:
        return redirect('teacher_dashboard')

    students = school_class.students.all()
    assignments = school_class.assignments.filter(status='active')

    student_stats = []
    for student_profile in students:
        student = student_profile.user

        variants = AssignmentVariant.objects.filter(
            student=student,
            assignment__in=assignments
        )

        total_correct = 0
        total_answers = 0

        for variant in variants:
            answers = variant.answers.all()
            total_correct += answers.filter(is_correct=True).count()
            total_answers += answers.count()

        percent = (total_correct / total_answers * 100) if total_answers > 0 else 0

        student_stats.append({
            'student': student,
            'total_assignments': variants.count(),
            'correct': total_correct,
            'total': total_answers,
            'percent': percent,
        })

    context = {
        'school_class': school_class,
        'student_stats': student_stats,
        'assignments': assignments,
    }
    return render(request, 'teacher/class_statistics.html', context)


# ===== УЧЕНИК: РЕШЕНИЕ РАБОТ И ПРОСМОТР РЕЗУЛЬТАТОВ =====

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    """Панель ученика"""
    student_profile = request.user.profile
    school_class = student_profile.school_class

    assignments = Assignment.objects.filter(
        school_class=school_class,
        status='active'
    ).order_by('-created_at')

    my_variants = AssignmentVariant.objects.filter(
        student=request.user
    ).select_related('assignment')

    variant_dict = {v.assignment_id: v for v in my_variants}

    assignments_with_status = []
    for assignment in assignments:
        variant = variant_dict.get(assignment.id)
        status = 'not_started'
        progress = 0

        if variant:
            answers = variant.answers.all()
            if answers.exists():
                status = 'started'
                correct = answers.filter(is_correct__isnull=False).count()
                total = answers.count()
                progress = (correct / total * 100) if total > 0 else 0

                if progress == 100:
                    status = 'completed'

        assignments_with_status.append({
            'assignment': assignment,
            'variant': variant,
            'status': status,
            'progress': progress,
        })

    context = {
        'school_class': school_class,
        'assignments': assignments_with_status,
    }
    return render(request, 'student/dashboard.html', context)


@login_required
@user_passes_test(is_student)
def solve_assignment(request, variant_id):
    """Решение проверочной работы"""
    variant = get_object_or_404(AssignmentVariant, id=variant_id, student=request.user)

    if request.method == 'POST':
        for question_num in range(1, len(variant.questions) + 1):
            answer_key = f'answer_{question_num}'
            if answer_key in request.POST:
                answer_text = request.POST.get(answer_key, '')

                StudentAnswer.objects.update_or_create(
                    variant=variant,
                    question_number=question_num,
                    defaults={'answer_text': answer_text}
                )

        return redirect('view_results', variant_id=variant.id)

    questions = variant.questions
    context = {
        'variant': variant,
        'questions': questions,
        'assignment': variant.assignment,
    }
    return render(request, 'student/solve_assignment.html', context)


@login_required
@user_passes_test(is_student)
def view_results(request, variant_id):
    """Просмотр результатов работы"""
    variant = get_object_or_404(AssignmentVariant, id=variant_id, student=request.user)
    answers = variant.answers.all().order_by('question_number')

    total = answers.count()
    correct = answers.filter(is_correct=True).count()
    checked = answers.filter(is_correct__isnull=False).count()

    percent = (correct / total * 100) if total > 0 else 0

    result_data = []
    for q_num, question in enumerate(variant.questions, 1):
        answer = answers.filter(question_number=q_num).first()

        result_data.append({
            'question_num': q_num,
            'question': question,
            'answer': answer,
            'student_answer': answer.answer_text if answer else '',
            'correct_answer': question.get('answer_text', ''),
            'is_correct': answer.is_correct if answer else None,
        })

    context = {
        'variant': variant,
        'assignment': variant.assignment,
        'result_data': result_data,
        'total': total,
        'correct': correct,
        'checked': checked,
        'percent': percent,
    }
    return render(request, 'student/view_results.html', context)


@login_required
@user_passes_test(is_student)
def my_statistics(request):
    """Личная статистика ученика"""
    student_profile = request.user.profile

    variants = AssignmentVariant.objects.filter(
        student=request.user
    ).select_related('assignment').order_by('-created_at')

    stats = {
        'total_assignments': variants.count(),
        'completed': 0,
        'total_correct': 0,
        'total_answers': 0,
        'average_percent': 0.0,
    }

    assignment_stats = []
    for variant in variants:
        answers = variant.answers.all()
        correct = answers.filter(is_correct=True).count()
        total = answers.count()

        if total > 0:
            percent = (correct / total * 100)
            stats['total_correct'] += correct
            stats['total_answers'] += total

            if percent == 100:
                stats['completed'] += 1

        assignment_stats.append({
            'assignment': variant.assignment,
            'correct': correct,
            'total': total,
            'percent': (correct / total * 100) if total > 0 else 0,
            'variant_id': variant.id,
        })

    if stats['total_answers'] > 0:
        stats['average_percent'] = (stats['total_correct'] / stats['total_answers'] * 100)

    context = {
        'stats': stats,
        'assignments': assignment_stats,
    }
    return render(request, 'student/my_statistics.html', context)


def is_teacher(user):
    """Проверяет, является ли пользователь учителем"""
    if not hasattr(user, 'profile'):
        return False
    return user.profile.role == 'teacher'


def is_student(user):
    """Проверяет, является ли пользователь учеником"""
    if not hasattr(user, 'profile'):
        return False
    return user.profile.role == 'student'


# ===== УЧИТЕЛЬ: УПРАВЛЕНИЕ РАБОТАМИ =====

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    """Панель управления учителя"""
    user = request.user
    classes = user.classes_teaching.all()

    assignments = Assignment.objects.filter(
        school_class__in=classes
    ).order_by('-created_at')

    context = {
        'classes': classes,
        'assignments': assignments,
        'user': user,
    }
    return render(request, 'teacher/dashboard.html', context)


@login_required
@user_passes_test(is_teacher)
def create_assignment(request, class_id):
    """Создание новой проверочной работы"""
    school_class = get_object_or_404(SchoolClass, id=class_id)

    # Проверяем, что это класс учителя
    if school_class.teacher != request.user:
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        topic_id = request.POST.get('topic')
        title = request.POST.get('title', '')

        topic = get_object_or_404(AssignmentTopic, id=topic_id, grade=school_class.grade)

        assignment = Assignment.objects.create(
            school_class=school_class,
            topic=topic,
            title=title or f'Работа по теме: {topic.name}',
            created_by=request.user
        )

        # Генерируем варианты для всех учеников класса
        generate_variants_for_assignment(assignment)

        return redirect('assignment_detail', assignment_id=assignment.id)

    topics = AssignmentTopic.objects.filter(grade=school_class.grade)
    context = {
        'school_class': school_class,
        'topics': topics,
    }
    return render(request, 'teacher/create_assignment.html', context)


def generate_variants_for_assignment(assignment):
    """Генерирует варианты заданий для всех учеников класса"""
    students = assignment.school_class.students.all()
    grade = assignment.school_class.grade.grade
    topic_name = assignment.topic.name

    for idx, student_profile in enumerate(students):
        student = student_profile.user
        variant_num = idx + 1

        # Выбираем генератор в зависимости от класса и темы
        if grade == '4':
            if 'Дроб' in topic_name or 'дроб' in topic_name:
                questions = generators.grade4_tasks.generate_assignment('fractions', num_questions=6)
            elif 'Процент' in topic_name or 'процент' in topic_name:
                questions = generators.grade4_tasks.generate_assignment('percentages', num_questions=6)
            else:
                questions = generators.grade4_tasks.generate_assignment('fractions', num_questions=6)
        elif grade == '5':
            if 'НОД' in topic_name:
                questions = grade5_tasks.generate_assignment('gcd', num_questions=4)
            elif 'НОК' in topic_name:
                questions = grade5_tasks.generate_assignment('lcm', num_questions=4)
            elif 'множител' in topic_name.lower():
                questions = grade5_tasks.generate_assignment('factorization', num_questions=3)
            else:
                questions = grade5_tasks.generate_assignment('mixed', num_questions=6)
        else:
            questions = []

        # Сохраняем вариант
        AssignmentVariant.objects.create(
            assignment=assignment,
            student=student,
            variant_number=variant_num,
            questions=questions
        )


@login_required
@user_passes_test(is_teacher)
def assignment_detail(request, assignment_id):
    """Просмотр деталей работы и статистики по классу"""
    assignment = get_object_or_404(Assignment, id=assignment_id)

    # Проверяем права доступа
    if assignment.school_class.teacher != request.user:
        return redirect('teacher_dashboard')

    # Получаем все варианты и статистику
    variants = assignment.variants.all().select_related('student')

    # Подсчитываем статистику
    stats = {
        'total_students': variants.count(),
        'submitted': 0,
        'total_correct': 0,
        'average_score': 0.0,
    }

    variant_data = []
    for variant in variants:
        answers = variant.answers.all()
        correct = answers.filter(is_correct=True).count()
        total = answers.count()

        percent = (correct / total * 100) if total > 0 else 0

        if answers.exists():
            stats['submitted'] += 1
            stats['total_correct'] += correct

        variant_data.append({
            'variant': variant,
            'student_name': variant.student.get_full_name(),
            'correct': correct,
            'total': total,
            'percent': percent,
        })

    if stats['submitted'] > 0:
        stats['average_score'] = stats['total_correct'] / (stats['submitted'] * len(variants[0].answers.all())) * 100 if variants else 0

    context = {
        'assignment': assignment,
        'variant_data': variant_data,
        'stats': stats,
    }
    return render(request, 'teacher/assignment_detail.html', context)


@login_required
@user_passes_test(is_teacher)
def regenerate_assignment_variants(request, assignment_id):
    """Перегенерирует варианты работы"""
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if assignment.school_class.teacher != request.user:
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        # Удаляем старые варианты и ответы
        AssignmentVariant.objects.filter(assignment=assignment).delete()

        # Генерируем новые
        generate_variants_for_assignment(assignment)

        return redirect('assignment_detail', assignment_id=assignment.id)

    context = {'assignment': assignment}
    return render(request, 'teacher/confirm_regenerate.html', context)


@login_required
@user_passes_test(is_teacher)
def class_statistics(request, class_id):
    """Статистика по классу"""
    school_class = get_object_or_404(SchoolClass, id=class_id)

    if school_class.teacher != request.user:
        return redirect('teacher_dashboard')

    students = school_class.students.all()
    assignments = school_class.assignments.filter(status='active')

    student_stats = []
    for student_profile in students:
        student = student_profile.user

        # Получаем все варианты ученика по активным работам
        variants = AssignmentVariant.objects.filter(
            student=student,
            assignment__in=assignments
        )

        total_correct = 0
        total_answers = 0

        for variant in variants:
            answers = variant.answers.all()
            total_correct += answers.filter(is_correct=True).count()
            total_answers += answers.count()

        percent = (total_correct / total_answers * 100) if total_answers > 0 else 0

        student_stats.append({
            'student': student,
            'total_assignments': variants.count(),
            'correct': total_correct,
            'total': total_answers,
            'percent': percent,
        })

    context = {
        'school_class': school_class,
        'student_stats': student_stats,
        'assignments': assignments,
    }
    return render(request, 'teacher/class_statistics.html', context)


# ===== УЧЕНИК: РЕШЕНИЕ РАБОТ И ПРОСМОТР РЕЗУЛЬТАТОВ =====

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    """Панель ученика"""
    student_profile = request.user.profile
    school_class = student_profile.school_class

    # Получаем все активные работы для класса
    assignments = Assignment.objects.filter(
        school_class=school_class,
        status='active'
    ).order_by('-created_at')

    # Получаем варианты ученика
    my_variants = AssignmentVariant.objects.filter(
        student=request.user
    ).select_related('assignment')

    variant_dict = {v.assignment_id: v for v in my_variants}

    assignments_with_status = []
    for assignment in assignments:
        variant = variant_dict.get(assignment.id)
        status = 'not_started'
        progress = 0

        if variant:
            answers = variant.answers.all()
            if answers.exists():
                status = 'started'
                correct = answers.filter(is_correct__isnull=False).count()
                total = answers.count()
                progress = (correct / total * 100) if total > 0 else 0

                if progress == 100:
                    status = 'completed'

        assignments_with_status.append({
            'assignment': assignment,
            'variant': variant,
            'status': status,
            'progress': progress,
        })

    context = {
        'school_class': school_class,
        'assignments': assignments_with_status,
    }
    return render(request, 'student/dashboard.html', context)


@login_required
@user_passes_test(is_student)
def solve_assignment(request, variant_id):
    """Решение проверочной работы"""
    variant = get_object_or_404(AssignmentVariant, id=variant_id, student=request.user)

    if request.method == 'POST':
        # Сохраняем ответы
        for question_num, answer_text in request.POST.items():
            if question_num.startswith('answer_'):
                q_num = int(question_num.split('_')[1])

                StudentAnswer.objects.update_or_create(
                    variant=variant,
                    question_number=q_num,
                    defaults={'answer_text': answer_text}
                )

        return redirect('view_results', variant_id=variant.id)

    questions = variant.questions
    context = {
        'variant': variant,
        'questions': questions,
        'assignment': variant.assignment,
    }
    return render(request, 'student/solve_assignment.html', context)


@login_required
@user_passes_test(is_student)
def view_results(request, variant_id):
    """Просмотр результатов работы"""
    variant = get_object_or_404(AssignmentVariant, id=variant_id, student=request.user)
    answers = variant.answers.all().order_by('question_number')

    # Подсчитываем результаты
    total = answers.count()
    correct = answers.filter(is_correct=True).count()
    checked = answers.filter(is_correct__isnull=False).count()

    percent = (correct / total * 100) if total > 0 else 0

    result_data = []
    for q_num, question in enumerate(variant.questions, 1):
        answer = answers.filter(question_number=q_num).first()

        result_data.append({
            'question_num': q_num,
            'question': question,
            'answer': answer,
            'student_answer': answer.answer_text if answer else '',
            'correct_answer': question.get('answer_text', ''),
            'is_correct': answer.is_correct if answer else None,
        })

    context = {
        'variant': variant,
        'assignment': variant.assignment,
        'result_data': result_data,
        'total': total,
        'correct': correct,
        'checked': checked,
        'percent': percent,
    }
    return render(request, 'student/view_results.html', context)


@login_required
@user_passes_test(is_student)
def my_statistics(request):
    """Личная статистика ученика"""
    student_profile = request.user.profile

    # Получаем все варианты ученика
    variants = AssignmentVariant.objects.filter(
        student=request.user
    ).select_related('assignment').order_by('-created_at')

    stats = {
        'total_assignments': variants.count(),
        'completed': 0,
        'total_correct': 0,
        'total_answers': 0,
        'average_percent': 0.0,
    }

    assignment_stats = []
    for variant in variants:
        answers = variant.answers.all()
        correct = answers.filter(is_correct=True).count()
        total = answers.count()

        if total > 0:
            percent = (correct / total * 100)
            stats['total_correct'] += correct
            stats['total_answers'] += total

            if percent == 100:
                stats['completed'] += 1

        assignment_stats.append({
            'assignment': variant.assignment,
            'correct': correct,
            'total': total,
            'percent': (correct / total * 100) if total > 0 else 0,
            'variant_id': variant.id,
        })

    if stats['total_answers'] > 0:
        stats['average_percent'] = (stats['total_correct'] / stats['total_answers'] * 100)

    context = {
        'stats': stats,
        'assignments': assignment_stats,
    }
    return render(request, 'student/my_statistics.html', context)

# assignments/views.py - Основные представления
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import (
    Assignment, AssignmentVariant, StudentAnswer,
    SchoolClass, UserProfile, AssignmentTopic
)


def is_teacher(user):
    """Проверяет, является ли пользователь учителем"""
    if not hasattr(user, 'profile'):
        return False
    return user.profile.role == 'teacher'


def is_student(user):
    """Проверяет, является ли пользователь учеником"""
    if not hasattr(user, 'profile'):
        return False
    return user.profile.role == 'student'


# ===== УЧИТЕЛЬ: УПРАВЛЕНИЕ РАБОТАМИ =====

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    """Панель управления учителя"""
    user = request.user
    classes = user.classes_teaching.all()

    assignments = Assignment.objects.filter(
        school_class__in=classes
    ).order_by('-created_at')

    context = {
        'classes': classes,
        'assignments': assignments,
        'user': user,
    }
    return render(request, 'teacher/dashboard.html', context)


@login_required
@user_passes_test(is_teacher)
def create_assignment(request, class_id):
    """Создание новой проверочной работы"""
    school_class = get_object_or_404(SchoolClass, id=class_id)

    if school_class.teacher != request.user:
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        topic_id = request.POST.get('topic')
        title = request.POST.get('title', '')

        topic = get_object_or_404(AssignmentTopic, id=topic_id, grade=school_class.grade)

        assignment = Assignment.objects.create(
            school_class=school_class,
            topic=topic,
            title=title or f'Работа по теме: {topic.name}',
            created_by=request.user
        )

        generate_variants_for_assignment(assignment)

        return redirect('assignment_detail', assignment_id=assignment.id)

    topics = AssignmentTopic.objects.filter(grade=school_class.grade)
    context = {
        'school_class': school_class,
        'topics': topics,
    }
    return render(request, 'teacher/create_assignment.html', context)


def generate_variants_for_assignment(assignment):
    """Генерирует варианты заданий для всех учеников класса"""
    try:
        from assignments.generators import grade4_tasks, grade5_tasks
    except ImportError:
        # Если генераторы не найдены, создаем пустые варианты
        students = assignment.school_class.students.all()
        for idx, student_profile in enumerate(students, 1):
            AssignmentVariant.objects.create(
                assignment=assignment,
                student=student_profile.user,
                variant_number=idx,
                questions=[]
            )
        return

    students = assignment.school_class.students.all()
    grade = assignment.school_class.grade.grade
    topic_name = assignment.topic.name

    for idx, student_profile in enumerate(students, 1):
        student = student_profile.user

        # Выбираем генератор
        if grade == '4':
            if 'Дроб' in topic_name or 'дроб' in topic_name:
                questions = grade4_tasks.generate_assignment('fractions', num_questions=6)
            elif 'Процент' in topic_name or 'процент' in topic_name:
                questions = grade4_tasks.generate_assignment('percentages', num_questions=6)
            else:
                questions = grade4_tasks.generate_assignment('fractions', num_questions=6)
        elif grade == '5':
            if 'НОД' in topic_name:
                questions = grade5_tasks.generate_assignment('gcd', num_questions=4)
            elif 'НОК' in topic_name:
                questions = grade5_tasks.generate_assignment('lcm', num_questions=4)
            elif 'множител' in topic_name.lower():
                questions = grade5_tasks.generate_assignment('factorization', num_questions=3)
            else:
                questions = grade5_tasks.generate_assignment('mixed', num_questions=6)
        else:
            questions = []

        AssignmentVariant.objects.create(
            assignment=assignment,
            student=student,
            variant_number=idx,
            questions=questions
        )


@login_required
@user_passes_test(is_teacher)
def assignment_detail(request, assignment_id):
    """Просмотр деталей работы и статистики по классу"""
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if assignment.school_class.teacher != request.user:
        return redirect('teacher_dashboard')

    variants = assignment.variants.all().select_related('student')

    stats = {
        'total_students': variants.count(),
        'submitted': 0,
        'total_correct': 0,
        'average_score': 0.0,
    }

    variant_data = []
    for variant in variants:
        answers = variant.answers.all()
        correct = answers.filter(is_correct=True).count()
        total = answers.count()

        percent = (correct / total * 100) if total > 0 else 0

        if answers.exists():
            stats['submitted'] += 1
            stats['total_correct'] += correct

        variant_data.append({
            'variant': variant,
            'student_name': variant.student.get_full_name(),
            'correct': correct,
            'total': total,
            'percent': percent,
        })

    context = {
        'assignment': assignment,
        'variant_data': variant_data,
        'stats': stats,
    }
    return render(request, 'teacher/assignment_detail.html', context)


@login_required
@user_passes_test(is_teacher)
def regenerate_assignment_variants(request, assignment_id):
    """Перегенерирует варианты работы"""
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if assignment.school_class.teacher != request.user:
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        AssignmentVariant.objects.filter(assignment=assignment).delete()
        generate_variants_for_assignment(assignment)
        return redirect('assignment_detail', assignment_id=assignment.id)

    context = {'assignment': assignment}
    return render(request, 'teacher/confirm_regenerate.html', context)


@login_required
@user_passes_test(is_teacher)
def class_statistics(request, class_id):
    """Статистика по классу"""
    school_class = get_object_or_404(SchoolClass, id=class_id)

    if school_class.teacher != request.user:
        return redirect('teacher_dashboard')

    students = school_class.students.all()
    assignments = school_class.assignments.filter(status='active')

    student_stats = []
    for student_profile in students:
        student = student_profile.user

        variants = AssignmentVariant.objects.filter(
            student=student,
            assignment__in=assignments
        )

        total_correct = 0
        total_answers = 0

        for variant in variants:
            answers = variant.answers.all()
            total_correct += answers.filter(is_correct=True).count()
            total_answers += answers.count()

        percent = (total_correct / total_answers * 100) if total_answers > 0 else 0

        student_stats.append({
            'student': student,
            'total_assignments': variants.count(),
            'correct': total_correct,
            'total': total_answers,
            'percent': percent,
        })

    context = {
        'school_class': school_class,
        'student_stats': student_stats,
        'assignments': assignments,
    }
    return render(request, 'teacher/class_statistics.html', context)


# ===== УЧЕНИК: РЕШЕНИЕ РАБОТ И ПРОСМОТР РЕЗУЛЬТАТОВ =====

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    """Панель ученика"""
    student_profile = request.user.profile
    school_class = student_profile.school_class

    assignments = Assignment.objects.filter(
        school_class=school_class,
        status='active'
    ).order_by('-created_at')

    my_variants = AssignmentVariant.objects.filter(
        student=request.user
    ).select_related('assignment')

    variant_dict = {v.assignment_id: v for v in my_variants}

    assignments_with_status = []
    for assignment in assignments:
        variant = variant_dict.get(assignment.id)
        status = 'not_started'
        progress = 0

        if variant:
            answers = variant.answers.all()
            if answers.exists():
                status = 'started'
                correct = answers.filter(is_correct__isnull=False).count()
                total = answers.count()
                progress = (correct / total * 100) if total > 0 else 0

                if progress == 100:
                    status = 'completed'

        assignments_with_status.append({
            'assignment': assignment,
            'variant': variant,
            'status': status,
            'progress': progress,
        })

    context = {
        'school_class': school_class,
        'assignments': assignments_with_status,
    }
    return render(request, 'student/dashboard.html', context)


@login_required
@user_passes_test(is_student)
def solve_assignment(request, variant_id):
    """Решение проверочной работы"""
    variant = get_object_or_404(AssignmentVariant, id=variant_id, student=request.user)

    if request.method == 'POST':
        for question_num in range(1, len(variant.questions) + 1):
            answer_key = f'answer_{question_num}'
            if answer_key in request.POST:
                answer_text = request.POST.get(answer_key, '')

                StudentAnswer.objects.update_or_create(
                    variant=variant,
                    question_number=question_num,
                    defaults={'answer_text': answer_text}
                )

        return redirect('view_results', variant_id=variant.id)

    questions = variant.questions
    context = {
        'variant': variant,
        'questions': questions,
        'assignment': variant.assignment,
    }
    return render(request, 'student/solve_assignment.html', context)


@login_required
@user_passes_test(is_student)
def view_results(request, variant_id):
    """Просмотр результатов работы"""
    variant = get_object_or_404(AssignmentVariant, id=variant_id, student=request.user)
    answers = variant.answers.all().order_by('question_number')

    total = answers.count()
    correct = answers.filter(is_correct=True).count()
    checked = answers.filter(is_correct__isnull=False).count()

    percent = (correct / total * 100) if total > 0 else 0

    result_data = []
    for q_num, question in enumerate(variant.questions, 1):
        answer = answers.filter(question_number=q_num).first()

        result_data.append({
            'question_num': q_num,
            'question': question,
            'answer': answer,
            'student_answer': answer.answer_text if answer else '',
            'correct_answer': question.get('answer_text', ''),
            'is_correct': answer.is_correct if answer else None,
        })

    context = {
        'variant': variant,
        'assignment': variant.assignment,
        'result_data': result_data,
        'total': total,
        'correct': correct,
        'checked': checked,
        'percent': percent,
    }
    return render(request, 'student/view_results.html', context)


@login_required
@user_passes_test(is_student)
def my_statistics(request):
    """Личная статистика ученика"""
    student_profile = request.user.profile

    variants = AssignmentVariant.objects.filter(
        student=request.user
    ).select_related('assignment').order_by('-created_at')

    stats = {
        'total_assignments': variants.count(),
        'completed': 0,
        'total_correct': 0,
        'total_answers': 0,
        'average_percent': 0.0,
    }

    assignment_stats = []
    for variant in variants:
        answers = variant.answers.all()
        correct = answers.filter(is_correct=True).count()
        total = answers.count()

        if total > 0:
            percent = (correct / total * 100)
            stats['total_correct'] += correct
            stats['total_answers'] += total

            if percent == 100:
                stats['completed'] += 1

        assignment_stats.append({
            'assignment': variant.assignment,
            'correct': correct,
            'total': total,
            'percent': (correct / total * 100) if total > 0 else 0,
            'variant_id': variant.id,
        })

    if stats['total_answers'] > 0:
        stats['average_percent'] = (stats['total_correct'] / stats['total_answers'] * 100)

    context = {
        'stats': stats,
        'assignments': assignment_stats,
    }
    return render(request, 'student/my_statistics.html', context)


def is_teacher(user):
    """Проверяет, является ли пользователь учителем"""
    if not hasattr(user, 'profile'):
        return False
    return user.profile.role == 'teacher'


def is_student(user):
    """Проверяет, является ли пользователь учеником"""
    if not hasattr(user, 'profile'):
        return False
    return user.profile.role == 'student'


# ===== УЧИТЕЛЬ: УПРАВЛЕНИЕ РАБОТАМИ =====

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    """Панель управления учителя"""
    user = request.user
    classes = user.classes_teaching.all()
    
    assignments = Assignment.objects.filter(
        school_class__in=classes
    ).order_by('-created_at')
    
    context = {
        'classes': classes,
        'assignments': assignments,
        'user': user,
    }
    return render(request, 'teacher/dashboard.html', context)


@login_required
@user_passes_test(is_teacher)
def create_assignment(request, class_id):
    """Создание новой проверочной работы"""
    school_class = get_object_or_404(SchoolClass, id=class_id)
    
    # Проверяем, что это класс учителя
    if school_class.teacher != request.user:
        return redirect('teacher_dashboard')
    
    if request.method == 'POST':
        topic_id = request.POST.get('topic')
        title = request.POST.get('title', '')
        
        topic = get_object_or_404(AssignmentTopic, id=topic_id, grade=school_class.grade)
        
        assignment = Assignment.objects.create(
            school_class=school_class,
            topic=topic,
            title=title or f'Работа по теме: {topic.name}',
            created_by=request.user
        )
        
        # Генерируем варианты для всех учеников класса
        generate_variants_for_assignment(assignment)
        
        return redirect('assignment_detail', assignment_id=assignment.id)
    
    topics = AssignmentTopic.objects.filter(grade=school_class.grade)
    context = {
        'school_class': school_class,
        'topics': topics,
    }
    return render(request, 'teacher/create_assignment.html', context)


def generate_variants_for_assignment(assignment):
    """Генерирует варианты заданий для всех учеников класса"""
    students = assignment.school_class.students.all()
    grade = assignment.school_class.grade.grade
    topic_name = assignment.topic.name
    
    for idx, student_profile in enumerate(students):
        student = student_profile.user
        variant_num = idx + 1
        
        # Выбираем генератор в зависимости от класса и темы
        if grade == '4':
            if 'Дроб' in topic_name or 'дроб' in topic_name:
                questions = generators.grade4_tasks.generate_assignment('fractions', num_questions=6)
            elif 'Процент' in topic_name or 'процент' in topic_name:
                questions = generators.grade4_tasks.generate_assignment('percentages', num_questions=6)
            else:
                questions = generators.grade4_tasks.generate_assignment('fractions', num_questions=6)
        elif grade == '5':
            if 'НОД' in topic_name:
                questions = grade5_tasks.generate_assignment('gcd', num_questions=4)
            elif 'НОК' in topic_name:
                questions = grade5_tasks.generate_assignment('lcm', num_questions=4)
            elif 'множител' in topic_name.lower():
                questions = grade5_tasks.generate_assignment('factorization', num_questions=3)
            else:
                questions = grade5_tasks.generate_assignment('mixed', num_questions=6)
        else:
            questions = []
        
        # Сохраняем вариант
        AssignmentVariant.objects.create(
            assignment=assignment,
            student=student,
            variant_number=variant_num,
            questions=questions
        )


@login_required
@user_passes_test(is_teacher)
def assignment_detail(request, assignment_id):
    """Просмотр деталей работы и статистики по классу"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Проверяем права доступа
    if assignment.school_class.teacher != request.user:
        return redirect('teacher_dashboard')
    
    # Получаем все варианты и статистику
    variants = assignment.variants.all().select_related('student')
    
    # Подсчитываем статистику
    stats = {
        'total_students': variants.count(),
        'submitted': 0,
        'total_correct': 0,
        'average_score': 0.0,
    }
    
    variant_data = []
    for variant in variants:
        answers = variant.answers.all()
        correct = answers.filter(is_correct=True).count()
        total = answers.count()
        
        percent = (correct / total * 100) if total > 0 else 0
        
        if answers.exists():
            stats['submitted'] += 1
            stats['total_correct'] += correct
        
        variant_data.append({
            'variant': variant,
            'student_name': variant.student.get_full_name(),
            'correct': correct,
            'total': total,
            'percent': percent,
        })
    
    if stats['submitted'] > 0:
        stats['average_score'] = stats['total_correct'] / (stats['submitted'] * len(variants[0].answers.all())) * 100 if variants else 0
    
    context = {
        'assignment': assignment,
        'variant_data': variant_data,
        'stats': stats,
    }
    return render(request, 'teacher/assignment_detail.html', context)


@login_required
@user_passes_test(is_teacher)
def regenerate_assignment_variants(request, assignment_id):
    """Перегенерирует варианты работы"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if assignment.school_class.teacher != request.user:
        return redirect('teacher_dashboard')
    
    if request.method == 'POST':
        # Удаляем старые варианты и ответы
        AssignmentVariant.objects.filter(assignment=assignment).delete()
        
        # Генерируем новые
        generate_variants_for_assignment(assignment)
        
        return redirect('assignment_detail', assignment_id=assignment.id)
    
    context = {'assignment': assignment}
    return render(request, 'teacher/confirm_regenerate.html', context)


@login_required
@user_passes_test(is_teacher)
def class_statistics(request, class_id):
    """Статистика по классу"""
    school_class = get_object_or_404(SchoolClass, id=class_id)
    
    if school_class.teacher != request.user:
        return redirect('teacher_dashboard')
    
    students = school_class.students.all()
    assignments = school_class.assignments.filter(status='active')
    
    student_stats = []
    for student_profile in students:
        student = student_profile.user
        
        # Получаем все варианты ученика по активным работам
        variants = AssignmentVariant.objects.filter(
            student=student,
            assignment__in=assignments
        )
        
        total_correct = 0
        total_answers = 0
        
        for variant in variants:
            answers = variant.answers.all()
            total_correct += answers.filter(is_correct=True).count()
            total_answers += answers.count()
        
        percent = (total_correct / total_answers * 100) if total_answers > 0 else 0
        
        student_stats.append({
            'student': student,
            'total_assignments': variants.count(),
            'correct': total_correct,
            'total': total_answers,
            'percent': percent,
        })
    
    context = {
        'school_class': school_class,
        'student_stats': student_stats,
        'assignments': assignments,
    }
    return render(request, 'teacher/class_statistics.html', context)


# ===== УЧЕНИК: РЕШЕНИЕ РАБОТ И ПРОСМОТР РЕЗУЛЬТАТОВ =====

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    """Панель ученика"""
    student_profile = request.user.profile
    school_class = student_profile.school_class
    
    # Получаем все активные работы для класса
    assignments = Assignment.objects.filter(
        school_class=school_class,
        status='active'
    ).order_by('-created_at')
    
    # Получаем варианты ученика
    my_variants = AssignmentVariant.objects.filter(
        student=request.user
    ).select_related('assignment')
    
    variant_dict = {v.assignment_id: v for v in my_variants}
    
    assignments_with_status = []
    for assignment in assignments:
        variant = variant_dict.get(assignment.id)
        status = 'not_started'
        progress = 0
        
        if variant:
            answers = variant.answers.all()
            if answers.exists():
                status = 'started'
                correct = answers.filter(is_correct__isnull=False).count()
                total = answers.count()
                progress = (correct / total * 100) if total > 0 else 0
                
                if progress == 100:
                    status = 'completed'
        
        assignments_with_status.append({
            'assignment': assignment,
            'variant': variant,
            'status': status,
            'progress': progress,
        })
    
    context = {
        'school_class': school_class,
        'assignments': assignments_with_status,
    }
    return render(request, 'student/dashboard.html', context)


@login_required
@user_passes_test(is_student)
def solve_assignment(request, variant_id):
    """Решение проверочной работы"""
    variant = get_object_or_404(AssignmentVariant, id=variant_id, student=request.user)
    
    if request.method == 'POST':
        # Сохраняем ответы
        for question_num, answer_text in request.POST.items():
            if question_num.startswith('answer_'):
                q_num = int(question_num.split('_')[1])
                
                StudentAnswer.objects.update_or_create(
                    variant=variant,
                    question_number=q_num,
                    defaults={'answer_text': answer_text}
                )
        
        return redirect('view_results', variant_id=variant.id)
    
    questions = variant.questions
    context = {
        'variant': variant,
        'questions': questions,
        'assignment': variant.assignment,
    }
    return render(request, 'student/solve_assignment.html', context)


@login_required
@user_passes_test(is_student)
def view_results(request, variant_id):
    """Просмотр результатов работы"""
    variant = get_object_or_404(AssignmentVariant, id=variant_id, student=request.user)
    answers = variant.answers.all().order_by('question_number')
    
    # Подсчитываем результаты
    total = answers.count()
    correct = answers.filter(is_correct=True).count()
    checked = answers.filter(is_correct__isnull=False).count()
    
    percent = (correct / total * 100) if total > 0 else 0
    
    result_data = []
    for q_num, question in enumerate(variant.questions, 1):
        answer = answers.filter(question_number=q_num).first()
        
        result_data.append({
            'question_num': q_num,
            'question': question,
            'answer': answer,
            'student_answer': answer.answer_text if answer else '',
            'correct_answer': question.get('answer_text', ''),
            'is_correct': answer.is_correct if answer else None,
        })
    
    context = {
        'variant': variant,
        'assignment': variant.assignment,
        'result_data': result_data,
        'total': total,
        'correct': correct,
        'checked': checked,
        'percent': percent,
    }
    return render(request, 'student/view_results.html', context)


@login_required
@user_passes_test(is_student)
def my_statistics(request):
    """Личная статистика ученика"""
    student_profile = request.user.profile
    
    # Получаем все варианты ученика
    variants = AssignmentVariant.objects.filter(
        student=request.user
    ).select_related('assignment').order_by('-created_at')
    
    stats = {
        'total_assignments': variants.count(),
        'completed': 0,
        'total_correct': 0,
        'total_answers': 0,
        'average_percent': 0.0,
    }
    
    assignment_stats = []
    for variant in variants:
        answers = variant.answers.all()
        correct = answers.filter(is_correct=True).count()
        total = answers.count()
        
        if total > 0:
            percent = (correct / total * 100)
            stats['total_correct'] += correct
            stats['total_answers'] += total
            
            if percent == 100:
                stats['completed'] += 1
        
        assignment_stats.append({
            'assignment': variant.assignment,
            'correct': correct,
            'total': total,
            'percent': (correct / total * 100) if total > 0 else 0,
            'variant_id': variant.id,
        })
    
    if stats['total_answers'] > 0:
        stats['average_percent'] = (stats['total_correct'] / stats['total_answers'] * 100)
    
    context = {
        'stats': stats,
        'assignments': assignment_stats,
    }
    return render(request, 'student/my_statistics.html', context)
