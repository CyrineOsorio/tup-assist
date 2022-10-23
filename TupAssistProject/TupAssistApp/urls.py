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

    # log out
    path('logout/', views.logoutUser, name= 'logout'),

    # studentregistration
    path('signup/', views.signup, name='signup'),

    # student
    path('student/', views.student, name='student'),

    # pic
    path('p-adding/', views.p_adding, name='p_adding'),

    # head
    path('h-adding/', views.h_adding, name='h_adding'),
    path('h-dropping/', views.h_dropping, name='h_dropping'),

    #registrar
    path('registrar/', views.registrar, name='registrar'),
    path('acc_cvs', views.acc_cvs, name='acc_cvs'),
    path('sub_cvs', views.sub_cvs, name='sub_cvs'),
    path('transStatus/<int:id>', views.transStatus),
    path('import_sched', views.import_sched, name='import_sched'),
    path('r-adding/', views.r_adding, name='r_adding'),
    path('r-adding/<int:id>', views.r_adding),
    path('r-dropping/', views.r_dropping, name='r_dropping'),
    path('r-transferring/', views.r_transferring, name='r_transferring'),
    
    #student
    path('student/', views.student, name='student'),
    path('s_adding', views.s_adding, name='s_adding'),
    path('s_adding_edit/<int:id>', views.s_adding_edit),
    path('s_adding_del/<int:id>', views.s_adding_del),
    path('s_dropping', views.s_dropping, name='s_dropping'),
    path('s_dropping_del/<int:id>', views.s_dropping_del),
    path('s_transferring', views.s_transferring, name='s_transferring'),
    path('s_transferring_del/<int:id>', views.s_transferring_del),

   
]