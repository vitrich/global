from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()




class PupilProfile(models.Model):
    CLASS_CHOICES = [
        ('5ВЭ', '5ВЭ'),
        ('5МИ', '5МИ'),
        ('5АВ', '5АВ'),
        ('5ЕМ', '5ЕМ'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    classname = models.CharField(
        max_length=20, 
        verbose_name="Класс", 
        choices=CLASS_CHOICES
    )
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    
    class Meta:
        verbose_name = "Профиль ученика"
        verbose_name_plural = "Профили учеников"
    
    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.classname})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # УПРОЩЕННАЯ ВЕРСИЯ



class Task(models.Model):
    topic_number = models.PositiveIntegerField(
        verbose_name="Номер темы"      # например, 1, 2, 3...
    )
    number = models.PositiveIntegerField(
        verbose_name="Номер задачи в теме"  # например, 1, 2, 3...
    )
    text = models.TextField(verbose_name="Текст задачи")
    correct_answer = models.CharField(max_length=100, verbose_name="Правильный ответ")

    class Meta:
        ordering = ["topic_number", "number"]
        unique_together = ("topic_number", "number")  # в одной теме не повторяются номера задач

    def __str__(self):
        return f"Т{self.topic_number} · Задача №{self.number}"

    

class TaskResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    given_answer = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class_name = models.CharField(max_length=20, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Результат задачи"
        verbose_name_plural = "Результаты задач"
    
    def __str__(self):
        return f"{self.user.username}: {self.task} ({'✅' if self.is_correct else '❌'})"
    
    def save(self, *args, **kwargs):
        if self.user and not self.class_name:
            try:
                self.class_name = self.user.pupilprofile.classname  # Исправлено!
            except PupilProfile.DoesNotExist:
                self.class_name = 'Неизвестно'
        super().save(*args, **kwargs)



from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Текст новости")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Автор")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")
    topic_number = models.PositiveIntegerField(null=True, blank=True, verbose_name="Тема (для сортировки)")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
    
    def __str__(self):
        return self.title[:50]