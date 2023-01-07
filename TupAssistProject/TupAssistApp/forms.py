from django.db.models import fields
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *

class HeadRegistration(UserCreationForm):
    class Meta:
        model = registration
        fields = ['studID','username', 'email', 'password1', 'password2', 'last_name', 'first_name','course', 'year', 'section', 'userType', 'department']
    
    def __init__(self, *args, **kwargs):
        super(HeadRegistration, self).__init__(*args, **kwargs)
        self.fields['course'].required = False
        self.fields['year'].required = False
        self.fields['section'].required = False
        self.fields['department'].required = False

