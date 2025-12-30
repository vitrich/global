# Обновленные модели для системы проверки знаний
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

    GRADE4_CHOICES = [
        ('НА', 'НА (Рыльская)'),
        ('МИ', 'МИ (Икаева)'),
        ('АА', 'АА (Баумгертнер)'),
        ('ВЭ', 'ВЭ (Гайдадина)'),
        ('ЕВ', 'ЕВ (Кострицкая)'),
    ]

    GRADE5_CHOICES = [
        ('МИ', 'МИ (Аношин)'),
        ('ВЭ', 'ВЭ (Тавриная)'),
        ('ЕВ', 'ЕВ (Гондарев)'),
        ('ЕМ', 'ЕМ (Карнаух)'),
        ('ИА', 'ИА (Новоженов)'),
    ]

    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=10)  # МИ, ВЭ, и т.д.
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                limit_choices_to={'groups__name': 'Учителя'},
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
    role = models.Ch