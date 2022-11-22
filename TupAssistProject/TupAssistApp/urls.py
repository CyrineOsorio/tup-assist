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


    # pic
    path('p-adding/', views.p_adding, name='p_adding'),
    path('p-adding-edit/<int:id>', views.p_adding_edit),

    # head
    path('h-adding/', views.h_adding, name='h_adding'),
    path('h-adding-edit/<int:id>', views.h_adding_edit),
    path('h-dropping/', views.h_dropping, name='h_dropping'),
    path('h-dropping-edit/<int:id>', views.h_dropping_edit),
    path('h-transferring/', views.h_transferring, name='h_transferring'),
    path('h-transferring-edit/<int:id>', views.h_transferring_edit),
    path('h-schedule/', views.h_schedule, name='h_schedule'),

    #registrar
    path('r_dashboard/', views.r_dashboard, name='r_dashboard'),
    path('acc_cvs', views.acc_cvs, name='acc_cvs'),
    path('sub_cvs', views.sub_cvs, name='sub_cvs'),
    path('transStatus/<int:id>', views.transStatus),
    path('import_sched', views.import_sched, name='import_sched'),
    path('r_adding/', views.r_adding, name='r_adding'),
    path('r_adding_view/<int:id>', views.r_adding_view),
    path('r_dropping/', views.r_dropping, name='r_dropping'),
    path('r_transferring/', views.r_transferring, name='r_transferring'),
    path('r_staff/', views.r_staff, name='r_staff'),
    path('r_staff_create', views.r_staff_create, name='r_staff_create'),
    
    
    
    #student
    path('s_adding', views.s_adding, name='s_adding'),
    path('s_step1_submit', views.s_step1_submit, name="s_step1_submit"),
    path('upload', views.upload, name='upload'),
    path('delupload', views.delupload, name='delupload'),
    path('s_adding_edit_sched', views.s_adding_edit_sched, name="s_adding_edit_sched"),
    path('s_step2_submit', views.s_step2_submit, name="s_step2_submit"),
    


    path('s_dropping', views.s_dropping, name='s_dropping'),
   

    path('s_transferring', views.s_transferring, name='s_transferring'),
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)