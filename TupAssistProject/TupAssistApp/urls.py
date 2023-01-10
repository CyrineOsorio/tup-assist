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


    #admin
    path('a_dashboard/', views.a_dashboard, name='a_dashboard'),
    path('student_acc_cvs', views.student_acc_cvs, name='student_acc_cvs'),
    path('staff_acc_cvs', views.staff_acc_cvs, name='staff_acc_cvs'),
    path('transStatus/<str:id>', views.transStatus),
    path('changestatus', views.changestatus, name='changestatus'),
    path('import_sched', views.import_sched, name='import_sched'),
    path('a_account/', views.a_account, name='a_account'),
    path('a_staff_create', views.a_staff_create, name='a_staff_create'),

    path('a_adding/', views.a_adding, name='a_adding'),
    path('a_approved_sub/<int:id>', views.a_approved_sub),

    path('a_dropping/', views.a_dropping, name='a_dropping'),
    path('a_approved_sub2/<int:id>', views.a_approved_sub2),

    path('a_transferring/', views.a_transferring, name='a_transferring'),
    path('a_approved_sub1/<int:id>', views.a_approved_sub1),



    # adaa
    path('adaa_profile/', views.adaa_profile, name='adaa_profile'),
    path('adaa_adding/', views.adaa_adding, name='adaa_adding'),
    path('adaa_adding_view/<str:studID>', views.adaa_adding_view),
    path('adaa_approved_sub/<int:id>', views.adaa_approved_sub),

    path('adaa_dropping/', views.adaa_dropping, name='adaa_dropping'),
    path('adaa_dropping_view/<str:studID>', views.adaa_dropping_view),
    path('r_edit_sub1', views.r_edit_sub1, name='r_edit_sub1'),
    path('adaa_dropping_approve', views.adaa_dropping_approve, name='adaa_dropping_approve'),
    
    
    path('adaa_transferring/', views.adaa_transferring, name='adaa_transferring'),
    path('adaa_transferring_view/<str:studID>', views.adaa_transferring_view),
    path('adaa_approved_sub2/<int:id>', views.adaa_approved_sub2),
    
    path('adaa_transferring_approve', views.adaa_transferring_approve, name='adaa_transferring_approve'),
    path('adaa_approved_sub1/<int:id>', views.adaa_approved_sub1),

   
    
    # head
    path('h_profile/', views.h_profile, name='h_profile'),
    path('changepassword2', views.changepassword2, name='changepassword2'),
    path('changeheadinfo', views.changeheadinfo, name='changeheadinfo'),

    path('h_subject/', views.h_subject, name='h_subject'),
    path('h_logs/', views.h_logs, name='h_logs'),
    path('sub_cvs', views.sub_cvs, name='sub_cvs'),

    path('h-adding/', views.h_adding, name='h_adding'),
    path('h_adding_edit/<str:studID>', views.h_adding_edit),
    path('h_edit_sub', views.h_edit_sub, name='h_edit_sub'),

    path('h-dropping/', views.h_dropping, name='h_dropping'),
    path('h_dropping_edit/<str:studID>', views.h_dropping_edit),
    path('h_edit_sub1', views.h_edit_sub1, name='h_edit_sub1'),

    path('h-transferring/', views.h_transferring, name='h_transferring'),
    path('h_transferring_edit/<str:studID>', views.h_transferring_edit),
    path('h_edit_sub2', views.h_edit_sub2, name='h_edit_sub2'),


    # pic
    path('p_profile/', views.p_profile, name='p_profile'),
    path('changepassword1', views.changepassword1, name='changepassword1'),
    path('changepicinfo', views.changepicinfo, name='changepicinfo'),

    path('p_adding/', views.p_adding, name='p_adding'),
    path('p_adding_edit/<str:studID>', views.p_adding_edit),
    path('p_edit_sub', views.p_edit_sub, name='p_edit_sub'),
    path('p_add_sub', views.p_add_sub, name='p_add_sub'),
    path('p_step1_submit', views.p_step1_submit, name='p_step1_submit'),
    path('p_requests/', views.p_requests, name='p_requests'),
    path('p_edit_sub1', views.p_edit_sub1, name='p_edit_sub1'),


    # teacher
    path('t_profile/', views.t_profile, name='t_profile'),
    path('t_requests/', views.t_requests, name='t_requests'),
    path('t_edit_sub', views.t_edit_sub, name='t_edit_sub'),
    


     #student
    path('s_profile', views.s_profile, name='s_profile'),
    path('changepassword', views.changepassword, name='changepassword'),
    path('changestudentinfo', views.changestudentinfo, name='changestudentinfo'),

    path('s_adding', views.s_adding, name='s_adding'),
    path('upload', views.upload, name='upload'),
    path('delupload', views.delupload, name='delupload'),
    path('upload1', views.upload1, name='upload1'),
    path('delupload1', views.delupload1, name='delupload1'),
    path('s_add_sub', views.s_add_sub, name='s_add_sub'),
    path('s_del_sub/<str:id>', views.s_del_sub),
    path('s_step1_submit', views.s_step1_submit, name="s_step1_submit"),
    # path('s_step2_submit', views.s_step2_submit, name="s_step2_submit"),
    path('s_edit_sub', views.s_edit_sub, name='s_edit_sub'),

    path('s_dropping', views.s_dropping, name='s_dropping'),
    path('s_drop_sub', views.s_drop_sub, name='s_drop_sub'),

    path('s_transferring', views.s_transferring, name='s_transferring'),
    path('s_trans_sub', views.s_trans_sub, name='s_trans_sub'),
    path('s_del_sub_t/<str:id>', views.s_del_sub_t),
    path('s_step1_submit_t', views.s_step1_submit_t, name="s_step1_submit_t"),
    
    
    
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)