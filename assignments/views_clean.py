# assignments/views.py - Скопируйте это
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import (
    Assignment, AssignmentVariant, StudentAnswer, 
    SchoolClass, UserProfile, AssignmentTopic
)


def is_teacher(user):
    if not hasattr(user, 'profile'):
        return False
    return user.profile.role == 'teacher'


def is_student(user):
    if not hasattr(user, 'profile'):
        return False
    return user.profile.role == 'student'


# ===== УЧИТЕЛЬ =====

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    user = request.user
    classes = user.classes_teaching.all()
    assignments = Assignment.objects.filter(school_class__in=classes).order_by('-created_at')
    
    return render(request, 'teacher/dashboard.html', {
        'classes': classes,
        'assignments': assignments,
        'user': user,
    })


@login_required
@user_passes_test(is_teacher)
def create_assignment(request, class_id):
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
            title=title or f'Работа: {topic.name}',
            created_by=request.user
        )
        
        generate_variants_for_assignment(assignment)
        return redirect('assignment_detail', assignment_id=assignment.id)
    
    topics = AssignmentTopic.objects.filter(grade=school_class.grade)
    return render(request, 'teacher/create_assignment.html', {
        'school_class': school_class,
        'topics': topics,
    })


def generate_variants_for_assignment(assignment):
    """Генерирует варианты для всех учеников класса"""
    students = assignment.school_class.students.all()
    
    for idx, student_profile in enumerate(students, 1):
        # Простые вопросы по умолчанию
        questions = [
            {
                'type': 'text',
                'text': f'Вопрос {i}',
                'answer': f'Ответ {i}',
                'answer_text': f'Ответ {i}'
            }
            for i in range(1, 4)
        ]
        
        AssignmentVariant.objects.create(
            assignment=assignment,
            student=student_profile.user,
            variant_number=idx,
            questions=questions
        )


@login_required
@user_passes_test(is_teacher)
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if assignment.school_class.teacher != request.user:
        return redirect('teacher_dashboard')
    
    variants = assignment.variants.all().select_related('student')
    
    stats = {'total_students': variants.count(), 'submitted': 0, 'total_correct': 0}
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
    
    return render(request, 'teacher/assignment_detail.html', {
        'assignment': assignment,
        'variant_data': variant_data,
        'stats': stats,
    })


@login_required
@user_passes_test(is_teacher)
def regenerate_assignment_variants(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if assignment.school_class.teacher != request.user:
        return redirect('teacher_dashboard')
    
    if request.method == 'POST':
        AssignmentVariant.objects.filter(assignment=assignment).delete()
        generate_variants_for_assignment(assignment)
        return redirect('assignment_detail', assignment_id=assignment.id)
    
    return render(request, 'teacher/confirm_regenerate.html', {'assignment': assignment})


@login_required
@user_passes_test(is_teacher)
def class_statistics(request, class_id):
    school_class = get_object_or_404(SchoolClass, id=class_id)
    
    if school_class.teacher != request.user:
        return redirect('teacher_dashboard')
    
    students = school_class.students.all()
    assignments = school_class.assignments.filter(status='active')
    
    student_stats = []
    for student_profile in students:
        variants = AssignmentVariant.objects.filter(student=student_profile.user, assignment__in=assignments)
        
        total_correct = 0
        total_answers = 0
        for variant in variants:
            answers = variant.answers.all()
            total_correct += answers.filter(is_correct=True).count()
            total_answers += answers.count()
        
        percent = (total_correct / total_answers * 100) if total_answers > 0 else 0
        
        student_stats.append({
            'student': student_profile.user,
            'total_assignments': variants.count(),
            'correct': total_correct,
            'total': total_answers,
            'percent': percent,
        })
    
    return render(request, 'teacher/class_statistics.html', {
        'school_class': school_class,
        'student_stats': student_stats,
        'assignments': assignments,
    })


# ===== УЧЕНИК =====

@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    student_profile = request.user.profile
    school_class = student_profile.school_class
    
    if not school_class:
        return redirect('/')
    
    assignments = Assignment.objects.filter(school_class=school_class, status='active').order_by('-created_at')
    my_variants = AssignmentVariant.objects.filter(student=request.user).select_related('assignment')
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
    
    return render(request, 'student/dashboard.html', {
        'school_class': school_class,
        'assignments': assignments_with_status,
    })


@login_required
@user_passes_test(is_student)
def solve_assignment(request, variant_id):
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
    
    return render(request, 'student/solve_assignment.html', {
        'variant': variant,
        'questions': variant.questions,
        'assignment': variant.assignment,
    })


@login_required
@user_passes_test(is_student)
def view_results(request, variant_id):
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
            'student_answer': answer.answer_text if answer else '',
            'correct_answer': question.get('answer_text', ''),
            'is_correct': answer.is_correct if answer else None,
        })
    
    return render(request, 'student/view_results.html', {
        'variant': variant,
        'assignment': variant.assignment,
        'result_data': result_data,
        'total': total,
        'correct': correct,
        'checked': checked,
        'percent': percent,
    })


@login_required
@user_passes_test(is_student)
def my_statistics(request):
    variants = AssignmentVariant.objects.filter(student=request.user).select_related('assignment').order_by('-created_at')
    
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
    
    return render(request, 'student/my_statistics.html', {
        'stats': stats,
        'assignments': assignment_stats,
    })
