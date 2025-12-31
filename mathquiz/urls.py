from django.urls import path
from . import views

app_name = 'mathquiz'

urlpatterns = [
    # Главная страница quiz
    path('', views.task_list, name='task_list'),

    # Задания (альтернативный путь)
    path('tasks/', views.task_list, name='task_list_alt'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/submit/', views.submit_answer, name='submit_answer'),

    # Личные кабинеты
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
]
