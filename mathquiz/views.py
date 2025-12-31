from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q, Count, Sum
from .models import Task, Topic, StudentProfile, StudentAnswer, SchoolClass

@login_required
def task_list(request):
    user = request.user
    is_student = hasattr(user, 'student_profile')
    is_teacher = SchoolClass.objects.filter(teacher=user).exists()
    topic_id = request.GET.get('topic')
    tasks = Task.objects.all()
    if topic_id: tasks = tasks.filter(topic_id=topic_id)
    topics = Topic.objects.all()
    return render(request, 'mathquiz/task_list.html', locals())

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if not hasattr(request.user, 'student_profile'): return redirect('task_list')
    previous_answers = StudentAnswer.objects.filter(student=request.user.student_profile, task=task).order_by('-attempted_at')
    return render(request, 'mathquiz/task_detail.html', locals())

@login_required
@require_http_methods(["POST"])
def submit_answer(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if not hasattr(request.user, 'student_profile'): return JsonResponse({'error': 'Только для учеников'}, status=403)
    answer = request.POST.get('answer', '').strip()
    is_correct = answer.lower() == task.correct_answer.strip().lower()
    score = task.score if is_correct else 0
    StudentAnswer.objects.create(student=request.user.student_profile, task=task, given_answer=answer, is_correct=is_correct, score_received=score)
    if is_correct:
        Task.objects.filter(id=task_id).update(correct_count=models.F('correct_count') + 1)
    return JsonResponse({'is_correct': is_correct, 'score_received': score, 'correct_answer': task.correct_answer})

@login_required
def student_dashboard(request):
    if not hasattr(request.user, 'student_profile'): return redirect('task_list')
    student = request.user.student_profile
    stats = StudentAnswer.objects.filter(student=student)
    total_score = stats.filter(is_correct=True).aggregate(Sum('score_received'))['score_received__sum'] or 0
    recent_answers = stats.order_by('-attempted_at')[:10]
    return render(request, 'mathquiz/student_dashboard.html', locals())

@login_required
def teacher_dashboard(request):
    classes = SchoolClass.objects.filter(teacher=request.user)
    return render(request, 'mathquiz/teacher_dashboard.html', locals())
