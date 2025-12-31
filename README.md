# MathQuiz

Django приложение для проверки знаний по математике.

## Установка
1. Добавьте 'mathquiz' в INSTALLED_APPS.
2. Подключите urls: path('quiz/', include('mathquiz.urls')).
3. python manage.py migrate
4. Создайте суперпользователя и добавьте данные через админку.
