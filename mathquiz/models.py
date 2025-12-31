from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator

class SchoolClass(models.Model):
    GRADE_CHOICES = ((4, "4 класс"), (5, "5 класс"))
    grade = models.PositiveSmallIntegerField(choices=GRADE_CHOICES, verbose_name="Класс")
    letter = models.CharField(max_length=1, blank=True, verbose_name="Буква")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="classes_as_teacher", verbose_name="Преподаватель", limit_choices_to={'is_teacher': True})
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("grade", "letter")
        verbose_name = "Класс"
        verbose_name_plural = "Классы"
    def __str__(self): return f"{self.grade}{self.letter}"

class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    school_class = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, blank=True, related_name="students")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: verbose_name = "Профиль ученика"; verbose_name_plural = "Профили учеников"
    def __str__(self): return self.user.get_full_name() or self.user.username

class Topic(models.Model):
    title = models.CharField(max_length=255, unique=True, verbose_name="Тема")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: verbose_name = "Тема"; verbose_name_plural = "Темы"
    def __str__(self): return self.title

class Task(models.Model):
    text = models.TextField(verbose_name="Текст")
    correct_answer = models.CharField(max_length=255, verbose_name="Ответ")
    score = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="Балл")
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    correct_count = models.PositiveIntegerField(default=0, verbose_name="Решено раз")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: verbose_name = "Задание"; verbose_name_plural = "Задания"
    def __str__(self): return f"Задание #{self.id}"

class StudentAnswer(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="answers")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="student_answers")
    given_answer = models.CharField(max_length=255)
    is_correct = models.BooleanField()
    score_received = models.PositiveIntegerField(default=0)
    attempted_at = models.DateTimeField(auto_now_add=True)
    class Meta: verbose_name = "Ответ"; verbose_name_plural = "Ответы"; ordering = ("-attempted_at",)
