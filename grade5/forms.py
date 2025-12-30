from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PupilProfile

 

class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, label="Имя", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=50, label="Фамилия", widget=forms.TextInput(attrs={'class': 'form-control'}))
    classname = forms.ChoiceField(
        choices=PupilProfile.CLASS_CHOICES,
        label="Класс", 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'classname', 'password1', 'password2')


class TaskAnswerForm(forms.Form):
    answer = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': True}),
        label="Ваш ответ"
    )
