# assignments/urls.py - URL-маршруты для системы проверки знаний
from django.urls import path
from . import views

urlpatterns = [
    # Общие страницы
    path('', views.student_dashboard, name='dashboard'),

    # Учитель
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/class/<int:class_id>/assignments/', views.teacher_dashboard, name='class_assignments'),
    path('teacher/class/<int:class_id>/statistics/', views.class_statistics, name='class_statistics'),
    path('teacher/assignment/create/<int:class_id>/', views.create_assignment, name='create_assignment'),
    path('teacher/assignment/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('teacher/assignment/<int:assignment_id>/regenerate/', views.regenerate_assignment_variants,
         name='regenerate_variants'),

    # Ученик
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/assignment/<int:variant_id>/solve/', views.solve_assignment, name='solve_assignment'),
    path('student/assignment/<int:variant_id>/results/', views.view_results, name='view_results'),
    path('student/statistics/', views.my_statistics, name='my_statistics'),
]
