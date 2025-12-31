from django.contrib import admin
from django.utils.html import format_html
from .models import SchoolClass, StudentProfile, Topic, Task, StudentAnswer

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ("__str__", "teacher", "created_at")
    list_filter = ("grade", "teacher")

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("__str__", "school_class")
    list_filter = ("school_class",)

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "topic", "score", "correct_count")
    list_filter = ("topic", "score")
    readonly_fields = ("correct_count",)

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ("student", "task", "is_correct", "score_received", "attempted_at")
    list_filter = ("is_correct", "attempted_at")
    readonly_fields = ("student", "task", "given_answer", "is_correct", "score_received")
