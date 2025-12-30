from django.contrib import admin
from .models import (
    Grade, SchoolClass, UserProfile, AssignmentTopic,
    Assignment, AssignmentVariant, StudentAnswer, AssignmentStats, StudentStats
)

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('grade',)

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('grade', 'name', 'teacher')
    list_filter = ('grade',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'school_class')
    list_filter = ('role', 'school_class')

@admin.register(AssignmentTopic)
class AssignmentTopicAdmin(admin.ModelAdmin):
    list_display = ('grade', 'number', 'name')
    list_filter = ('grade',)

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'school_class', 'topic', 'status', 'created_at')
    list_filter = ('status', 'school_class', 'created_at')
    search_fields = ('title',)

@admin.register(AssignmentVariant)
class AssignmentVariantAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'variant_number', 'created_at')
    list_filter = ('assignment', 'created_at')
    search_fields = ('student__username',)

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('variant', 'question_number', 'is_correct', 'submitted_at')
    list_filter = ('is_correct', 'submitted_at')

admin.site.register(AssignmentStats)
admin.site.register(StudentStats)
from django.contrib import admin

# Register your models here.
