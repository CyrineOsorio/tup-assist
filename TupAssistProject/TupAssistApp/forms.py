from django.db.models import fields
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *

class StudentRegistration(UserCreationForm):
    class Meta:
        model = StudentAccount
        fields = ['username', 'email', 'password1', 'password2', 'lname', 'fname', 'yrandsec', 'course', 'studID', 'userType']