from django.contrib import admin
from .models import News, Task, TaskResult, PupilProfile

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'is_published', 'topic_number']
    list_filter = ['is_published', 'created_at', 'topic_number']
    search_fields = ['title', 'content']

@admin.register(PupilProfile)
class PupilProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'last_name', 'first_name', 'classname']
    list_filter = ['classname']
    search_fields = ['last_name', 'first_name', 'user__username']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['topic_number', 'number', 'text']
    list_filter = ['topic_number']

@admin.register(TaskResult)
class TaskResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'is_correct', 'created_at']
    list_filter = ['is_correct', 'created_at']
    list_select_related = ['user', 'task']
