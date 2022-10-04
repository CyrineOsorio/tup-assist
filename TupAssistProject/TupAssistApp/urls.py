from os import name
from django.urls import path, re_path
from django.conf.urls import static
from django.conf import settings
from django.conf.urls.static import static
from . import views

from .views  import *


app_name = 'TupAssistApp'

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('student/', views.student, name='student'),
    path('registrar/', views.registrar, name='registrar'),
    path('sub_cvs', views.sub_cvs, name='sub_cvs'),
    path('transStatus/<int:id>', views.transStatus),
    
]