
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from django.contrib.auth.decorators import login_required

from .models import Task, TaskResult
from .forms import TaskAnswerForm
from .forms import RegistrationForm
from django.contrib.auth import authenticate, login, logout

def grade5_home(request):
    return render(request, 'grade5/home.html')

# В конец grade5/views.py
def gcd_trainer(request):
    """Статическая страница тренажёр НОД"""
    return render(request, 'grade5/gcd_trainer.html')


def grade5_register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = PupilProfile.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                classname=form.cleaned_data['classname']
            )
            login(request, user)
            messages.success(request, "Аккаунт создан! Добро пожаловать!")
            return redirect("grade5_home")
    else:
        form = RegistrationForm()
    return render(request, "grade5/register.html", {"form": form})


def grade5_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)  # проверка логина/пароля [web:501][web:548]
        if user is not None:
            login(request, user)
            messages.success(request, "Вы успешно вошли.")
            return redirect("grade5_home")
        else:
            messages.error(request, "Неверное имя пользователя или пароль.")
    return render(request, "grade5/login.html")

 
@login_required
def grade5_logout(request):
    logout(request)  # завершает сессию пользователя [web:501][web:539]
    return redirect("grade5_home")



@login_required
def grade5_results(request):
    results = (TaskResult.objects
        .filter(user=request.user)
        .select_related("task")
        .order_by("-created_at"))
    return render(request, "grade5/results.html", {"results": results})



@login_required
def grade5_solve(request):
    tasks = Task.objects.all().order_by("topic_number", "number")
    
    if request.user.is_authenticated:
        profile = request.user.pupilprofile
        solved_task_ids = set(TaskResult.objects
            .filter(user=request.user)
            .values_list('task_id', flat=True))
        
        tasks_with_status = []
        for task in tasks:
            tasks_with_status.append({
                'task': task,
                'is_solved': task.id in solved_task_ids
            })
    else:
        tasks_with_status = [{'task': task, 'is_solved': False} for task in tasks]
    
    return render(request, "grade5/solve_list.html", {
        'tasks_with_status': tasks_with_status,
        'user_class': getattr(request.user.pupilprofile, 'classname', None) if request.user.is_authenticated else None
    })


@login_required
def grade5_solve_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    is_solved = TaskResult.objects.filter(user=request.user, task=task).exists()
    
    if request.method == "POST":
        form = TaskAnswerForm(request.POST)
        if form.is_valid():
            TaskResult.objects.create(
                user=request.user,
                task=task,
                given_answer=form.cleaned_data['answer'],
                is_correct=form.cleaned_data['answer'] == task.correct_answer
            )
            messages.success(request, "Ответ отправлен!")
            return redirect('grade5_results')
    else:
        form = TaskAnswerForm()
    
    return render(request, 'grade5/solve_task.html', {
        'task': task, 
        'form': form,
        'is_solved': is_solved  # Важно!
    })


from .models import News
@login_required
def grade5_news(request):
    news_list = News.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'grade5/news.html', {'news_list': news_list})

@login_required
def grade5_news_add(request):
    if request.method == 'POST':
        news = News.objects.create(
            title=request.POST['title'],
            content=request.POST['content'],
            author=request.user,
            topic_number=request.POST.get('topic_number', None)
        )
        messages.success(request, "Новость добавлена!")
        return redirect('grade5_news')
    return render(request, 'grade5/news_add.html')


def grade5_class_stats(request):
    from django.db.models import Count
    
    class_stats = (PupilProfile.objects
        .values('classname')
        .annotate(count=Count('user'))
        .order_by('-count'))
    
    return render(request, 'grade5/class_stats.html', {'class_stats': class_stats})


from .models import PupilProfile, TaskResult

from django.db import models
from django.db.models import Count, Q  # ← ИСПРАВЛЕННЫЕ ИМПОРТЫ

@login_required
def grade5_class_stats(request):
    # Статистика учеников по классам
    class_stats = (PupilProfile.objects
        .values('classname')
        .annotate(pupils_count=Count('user'))
        .order_by('-pupils_count'))
    
    # Статистика решений по классам
    class_solutions = (TaskResult.objects
        .filter(user__pupilprofile__isnull=False)
        .values('user__pupilprofile__classname')
        .annotate(
            solutions_count=Count('id'),
            correct_count=Count('id', filter=Q(is_correct=True))  # ✅ Исправлено
        )
        .order_by('-solutions_count'))
    
    context = {
        'class_stats': class_stats,
        'class_solutions': class_solutions,
    }
    return render(request, 'grade5/class_stats.html', context)
