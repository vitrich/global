# ПОЛНЫЙ ФАЙЛ: assignments/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


# ===== КЛАССЫ И ПРЕПОДАВАТЕЛИ =====

class Grade(models.Model):
    """Параллель (4 класс или 5 класс)"""
    GRADE_CHOICES = [('4', '4 класс'), ('5', '5 класс')]

    grade = models.CharField(max_length=1, choices=GRADE_CHOICES, unique=True)

    def __str__(self):
        return f"{self.grade} класс"

    class Meta:
        verbose_name = "Параллель"
        verbose_name_plural = "Параллели"


class SchoolClass(models.Model):
    """Класс (группа) учеников"""
    # 5 класс: МИ, ВЭ, ЕВ, ЕМ, ИА
    # 4 класс: НА, МИ, АА, ВЭ, ЕВ

    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=10)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                related_name='classes_teaching')

    def __str__(self):
        return f"{self.grade} {self.name}"

    class Meta:
        verbose_name = "Класс"
        verbose_name_plural = "Классы"
        unique_together = ('grade', 'name')


class UserProfile(models.Model):
    """Профиль пользователя (ученик или учитель)"""
    ROLE_CHOICES = [
        ('student', 'Ученик'),
        ('teacher', 'Учитель'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     related_name='students',
                                     help_text="Для учеников - их класс")

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"


# ===== ПРОВЕРОЧНЫЕ РАБОТЫ И ЗАДАНИЯ =====

class AssignmentTopic(models.Model):
    """Тема для проверочной работы"""

    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.grade} - {self.name}"

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"
        unique_together = ('grade', 'number')
        ordering = ['grade', 'number']


class Assignment(models.Model):
    """Проверочная работа"""
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('active', 'Активна'),
        ('closed', 'Завершена'),
    ]

    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE,
                                     related_name='assignments')
    topic = models.ForeignKey(AssignmentTopic, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.school_class} - {self.topic} ({self.title})"

    class Meta:
        verbose_name = "Проверочная работа"
        verbose_name_plural = "Проверочные работы"
        ordering = ['-created_at']


class AssignmentVariant(models.Model):
    """Вариант проверочной работы для ученика"""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE,
                                   related_name='variants')
    student = models.ForeignKey(User, on_delete=models.CASCADE,
                                related_name='assignment_variants')
    variant_number = models.PositiveIntegerField()

    questions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.assignment} - {self.student.username} (В{self.variant_number})"

    class Meta:
        verbose_name = "Вариант работы"
        verbose_name_plural = "Варианты работ"
        unique_together = ('assignment', 'student', 'variant_number')


class StudentAnswer(models.Model):
    """Ответ ученика на задание"""
    variant = models.ForeignKey(AssignmentVariant, on_delete=models.CASCADE,
                                related_name='answers')
    question_number = models.PositiveIntegerField()
    answer_text = models.TextField()
    is_correct = models.BooleanField(null=True, blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    checked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.variant} - Q{self.question_number}"

    class Meta:
        verbose_name = "Ответ ученика"
        verbose_name_plural = "Ответы учеников"
        unique_together = ('variant', 'question_number')


# ===== СТАТИСТИКА =====

class AssignmentStats(models.Model):
    """Статистика по проверочной работе для класса"""
    assignment = models.OneToOneField(Assignment, on_delete=models.CASCADE)

    total_submitted = models.PositiveIntegerField(default=0)
    total_correct = models.PositiveIntegerField(default=0)
    average_score = models.FloatField(default=0.0)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Статистика: {self.assignment}"

    class Meta:
        verbose_name = "Статистика работы"
        verbose_name_plural = "Статистики работ"


class StudentStats(models.Model):
    """Статистика ученика по всем работам"""
    student = models.OneToOneField(User, on_delete=models.CASCADE,
                                   related_name='student_stats')

    total_assignments = models.PositiveIntegerField(default=0)
    completed_assignments = models.PositiveIntegerField(default=0)
    average_score = models.FloatField(default=0.0)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Статистика: {self.student.username}"

    class Meta:
        verbose_name = "Статистика ученика"
        verbose_name_plural = "Статистики учеников"
