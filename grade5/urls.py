from django.urls import path
from . import views

# hihi
urlpatterns = [
    path('', views.grade5_home, name='grade5_home'),
    path('register/', views.grade5_register, name='grade5_register'),
    path('login/', views.grade5_login, name='grade5_login'),
    path('logout/', views.grade5_logout, name='grade5_logout'),
    path("solve/", views.grade5_solve, name="grade5_solve"),
    path("solve/<int:task_id>/", views.grade5_solve_task, name="grade5_solve_task"),
    path("results/", views.grade5_results, name="grade5_results"),
    path('news/', views.grade5_news, name='grade5_news'),
    path('news/add/', views.grade5_news_add, name='grade5_news_add'),
    path('stats/', views.grade5_class_stats, name='grade5_class_stats'),
    path('gcd-trainer/', views.gcd_trainer, name='gcd_trainer'),
]

