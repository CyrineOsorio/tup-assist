from os import name
from django.urls import path, re_path
from django.conf.urls import static
from django.conf import settings
from django.conf.urls.static import static
from . import views

from .views  import *


app_name = 'TupAssistApp'

urlpatterns = [
    # Login
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),

    # Logout
    path('logout/', views.logoutUser, name= 'logout'),


    #registrar
    path('r_dashboard/', views.r_dashboard, name='r_dashboard'),
    path('student_acc_cvs', views.student_acc_cvs, name='student_acc_cvs'),
    path('staff_acc_cvs', views.staff_acc_cvs, name='staff_acc_cvs'),
    path('transStatus/<int:id>', views.transStatus),
    path('changestatus', views.changestatus, name='changestatus'),
    path('import_sched', views.import_sched, name='import_sched'),
    path('r_adding/', views.r_adding, name='r_adding'),
    path('r_adding_view/<int:studID>', views.r_adding_view),
    path('r_edit_sub', views.r_edit_sub, name='r_edit_sub'),
    path('r_dropping/', views.r_dropping, name='r_dropping'),
    path('r_transferring/', views.r_transferring, name='r_transferring'),
    path('r_account/', views.r_account, name='r_account'),
    path('r_staff_create', views.r_staff_create, name='r_staff_create'),

    #student
    path('s_profile', views.s_profile, name='s_profile'),
    path('changepassword', views.changepassword, name='changepassword'),
    path('changestudentinfo', views.changestudentinfo, name='changestudentinfo'),

    path('s_adding', views.s_adding, name='s_adding'),
    path('upload', views.upload, name='upload'),
    path('delupload', views.delupload, name='delupload'),
    path('s_add_sub', views.s_add_sub, name='s_add_sub'),
    path('s_del_sub/<int:id>', views.s_del_sub),
    path('s_step1_submit', views.s_step1_submit, name="s_step1_submit"),
    # path('s_step2_submit', views.s_step2_submit, name="s_step2_submit"),
    # path('s_edit_sub', views.s_edit_sub, name='s_edit_sub'),

    path('s_dropping', views.s_dropping, name='s_dropping'),
    path('s_drop_sub', views.s_drop_sub, name='s_drop_sub'),

    path('s_transferring', views.s_transferring, name='s_transferring'),

   


    # pic
    path('p_profile/', views.p_profile, name='p_profile'),
    path('changepassword1', views.changepassword1, name='changepassword1'),
    path('changepicinfo', views.changepicinfo, name='changepicinfo'),

    path('p_adding/', views.p_adding, name='p_adding'),
    path('p_adding_edit/<int:studID>', views.p_adding_edit),
    path('p_edit_sub', views.p_edit_sub, name='p_edit_sub'),
    path('p_add_sub', views.p_add_sub, name='p_add_sub'),
    path('p_step1_submit', views.p_step1_submit, name='p_step1_submit'),
    

    # head
    path('h_profile/', views.h_profile, name='h_profile'),
    path('changepassword2', views.changepassword2, name='changepassword2'),
    path('changeheadinfo', views.changeheadinfo, name='changeheadinfo'),

    path('h_subject/', views.h_subject, name='h_subject'),
    path('sub_cvs', views.sub_cvs, name='sub_cvs'),

    path('h-adding/', views.h_adding, name='h_adding'),
    path('h_adding_edit/<int:studID>', views.h_adding_edit),
    path('h_edit_sub', views.h_edit_sub, name='h_edit_sub'),

    path('h-dropping/', views.h_dropping, name='h_dropping'),
    path('h-dropping-edit/<int:studID>', views.h_dropping_edit),
    path('h-transferring/', views.h_transferring, name='h_transferring'),
    path('h-transferring-edit/<int:studID>', views.h_transferring_edit),
    
    
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)