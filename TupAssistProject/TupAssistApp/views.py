from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import redirect, render
#from pyexpat.errors import messages
from django.contrib import messages

from .models import *
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

import csv

import os
import time
from datetime import datetime


# importing pandas module
import pandas as pd

from itertools import chain

# filter "AND,OR,NOT"
from django.db.models import Q

from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.conf import settings

# Create your views here.
installed_apps = ['TupAssistApp']



#LOGIN PAGE
def index(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password) 

        if user is not None and user.is_superuser == True:
            login(request, user)
            return redirect('/a_dashboard')

        elif user is not None and user.userType == 'Assist. Director of Academic Affairs':
            login(request, user)
            return redirect('/adaa_adding')

        elif user is not None and user.userType == 'Student':
            login(request, user)
            return redirect('/s_profile')
        
        elif user is not None and user.userType == 'Department Head':
            login(request, user)
            return redirect('/h_profile')

        elif user is not None and user.userType == 'Program-in-charge':
            login(request, user)
            return redirect('/p_profile')
            
        elif user is not None and user.userType == 'Teacher':
            login(request, user)
            return redirect('/t_profile')
        else:
           messages.error(request, 'Invalid Credentials')
    return render(request, 'TupAssistApp/index.html')


#LOG OUT
def logoutUser(request):
    logout(request)
    return redirect('/index')




# CUSTOMIZE ADMIN PAGES

def a_dashboard(request):
    current_user = request.user
    subs = Subjects.objects.all()
    status = TransStatus.objects.all()
    sched = Schedule.objects.all()
    student = registration.objects.filter(userType='Student')
    context = {
        'current_user': current_user,
        'subs': subs,
        'status' : status,
        'sched': sched,
        'student': student
    }
    return render(request, 'TupAssistApp/a_dashboard.html', context)

def import_sched(request):
    if request.method=='POST': 
        junk = Schedule.objects.all()
        junk.delete()
        gSheetLink = request.POST.get('gSheetLink')
        school_year = request.POST.get('school_year')
        semester = request.POST.get('semester')
        data = Schedule.objects.create(gSheetLink = gSheetLink, school_year = school_year, semester = semester)
        data.save()
        return redirect('/a_dashboard')

def transStatus(request,id):
    status = TransStatus.objects.get(id=id)
    print(status)
    if status.status == 'Open':
        status1 = 'Close'
        status.status = status1
        status.save()
        print(status)
        return redirect('/a_dashboard')
    else:
        status.status = 'Open'
        status.save()
        return redirect('/a_dashboard')

def changestatus(request):
    TransName = request.POST.get('TransName')
    if request.method=='POST': 
        status = TransStatus.objects.get(TransName=TransName)
        status.school_year = request.POST.get('school_year')
        status.semester = request.POST.get('semester')
        status.status = request.POST.get('status')
        status.save()
        messages.success(request, 'Status Change Successfully')
        return redirect('/a_dashboard')


def a_account(request):
    current_user = request.user
    form = HeadRegistration()
    staff = registration.objects.filter(Q(userType='Department Head') | Q(userType='Program-in-Charge') | Q(userType='Teacher') | Q(userType='Assist. Director of Academic Affairs'))
    student = registration.objects.filter(userType='Student')
    context = {
        'form': form,
        'current_user': current_user,
        'student': student,
        'staff': staff
    }
    if request.method == 'POST':
        form = HeadRegistration(request.POST)
        if form.is_valid():
            form.save()
            return redirect ('/a_account')
        else:
            messages.error(request, 'Invalid Credentials!')
    return render(request, 'TupAssistApp/a_account.html', context)

def student_acc_cvs(request):
    if request.method=='POST':
        junk = registration.objects.filter(userType='Student')
        junk.delete()
        form = StudentRegistration(request.POST)
        studcvsfile = request.FILES["studcvsfile"]
        decoded_file = studcvsfile.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)
        print(reader)
        for row in reader:
            try:
                new_revo = registration.objects.create(studID=str(row[0]), username=str(row[3]), email=str(row[3]), first_name=str(row[1]), last_name=str(row[2]), userType='Student')
                new_revo.set_password('TUPC-'+str(row[0])) #Default Password
                new_revo.save()    
                messages.success(request, 'Successfully Import, but check if data imported is correct.')
            except:
                messages.error(request, 'it looks like CSV format is not match to the table.')
                return redirect('/a_account')
        return redirect('/a_account')
    return redirect('/a_account')

def staff_acc_cvs(request):
    if request.method=='POST':
        junk = registration.objects.filter(Q(userType='Department Head') | Q(userType='Program-in-Charge'))
        junk.delete()
        form = StudentRegistration(request.POST)
        staffcvsfile = request.FILES["staffcvsfile"]
        decoded_file = staffcvsfile.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)
        print(reader)
        for row in reader:
            try:
                new_revo = registration.objects.create(studID=str(row[0]), username=str(row[3]), email=str(row[3]), first_name=str(row[1]), last_name=str(row[2]), userType=str(row[4]), department=str(row[5]))
                new_revo.set_password('TUPC-'+str(row[0])) #Default Password
                new_revo.save()    
                messages.success(request, 'Successfully Import, but check if data imported is correct.')
            except:
                messages.error(request, 'it looks like CSV format is not match to the table.')
                return redirect('/a_account')
        return redirect('/a_account')
    return redirect('/a_account')

def a_staff_create(request):
    form = HeadRegistration(request.POST)
    if form.is_valid():
        form.save()
        messages.error(request, 'Account Successfully Created!')
        return redirect ('/a_staff')
    else:
        messages.error(request, 'Invalid Credentials!')
        return redirect ('/a_staff')
    return render(request, 'TupAssistApp/a_staff.html')

def a_adding(request):
    current_user = request.user = request.user
    req = AddingReq.objects.all()
    context = { 
        'req': req,
        'current_user': current_user,
        }
    return render(request, 'TupAssistApp/a_adding.html', context)

def a_dropping(request):
    current_user = request.user
    req = DroppingReq.objects.all()
    context = {
        'req': req,
        'current_user': current_user
        }
    return render(request, 'TupAssistApp/a_dropping.html', context)

def a_transferring(request):
    current_user = request.user
    req = TransferringReq.objects.all()
    context = { 
        'req': req,
        'current_user': current_user
        }
    return render(request, 'TupAssistApp/a_transferring.html', context)






# ADAA PAGES

def adaa_profile(request):
    current_user = request.user
    form = PasswordChangeForm(current_user)
    # Models
    context = {
        'current_user': current_user,
        'form': form
    }
    return render(request, 'TupAssistApp/adaa_profile.html', context)

def adaa_adding(request):
    current_user = request.user = request.user
    test = registration.objects.filter(userType='Student')
    context = { 
        'test': test,
        'current_user': current_user,
        }
    return render(request, 'TupAssistApp/adaa_adding.html', context)

def adaa_adding_view(request, studID):
    current_user = request.user
    data = registration.objects.get(studID=studID)
    req = AddingReq.objects.filter(studID=data.studID)
    context = { 
        'req': req,
        'current_user': current_user,
        'student_info': data,
        }
    return render(request, 'TupAssistApp/adaa_adding_view.html', context)

def r_edit_sub(request):
    studID = request.POST.get('studID')
    data = registration.objects.get(studID=studID)
    if request.method =='POST':
        id = request.POST.get('id')   
        edit = AddingReq.objects.get(id=id) 
        edit.admin_approve = request.POST.get('admin_approve')
        edit.admin_name = request.POST.get('admin_name')
        edit.admin_date = datetime.now()
        edit.save()
        messages.success(request, 'Request Successfully Edited!')
        return redirect('/adaa_adding_view/'+ str(data.studID))


def adaa_dropping(request):
    current_user = request.user
    test = registration.objects.filter(userType='Student')
    context = {
        'test': test,
        'current_user': current_user
        }
    return render(request, 'TupAssistApp/adaa_dropping.html', context)

def adaa_dropping_view(request, studID):
    current_user = request.user
    data = registration.objects.get(studID=studID)
    req = DroppingReq.objects.filter(studID=data.studID)
    context = { 
        'req': req,
        'current_user': current_user,
        'student_info': data,
        }
    return render(request, 'TupAssistApp/adaa_dropping_view.html', context)

def r_edit_sub1(request):
    studID = request.POST.get('studID')
    data = registration.objects.get(studID=studID)
    if request.method =='POST':
        id = request.POST.get('id')   
        edit = DroppingReq.objects.get(id=id) 
        edit.admin_approve = request.POST.get('admin_approve')
        edit.admin_name = request.POST.get('admin_name')
        edit.admin_date = datetime.now()
        edit.save()
        messages.success(request, 'Request Successfully Edited!')
        return redirect('/adaa_dropping_view/'+ str(data.studID))

def adaa_transferring(request):
    current_user = request.user
    test = registration.objects.filter(userType='Student')
    context = { 
        'test': test,
        'current_user': current_user
        }
    return render(request, 'TupAssistApp/adaa_transferring.html', context)




#STUDENT PAGES

def s_profile(request):
    current_user = request.user
    form = PasswordChangeForm(current_user)
    # Models
    context = {
        'current_user': current_user,
        'form': form
    }
    return render(request, 'TupAssistApp/s_profile.html', context)

def changepassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Change Password Successfully')
            return redirect('/s_profile')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('/s_profile')

def changestudentinfo(request):
    current_user = request.user
    if request.method == 'POST':
        try:
            data = registration.objects.get(username=current_user.username)
            data.course = request.POST.get("course")
            data.year = request.POST.get("year")
            data.section = request.POST.get("section")
            data.studID = request.POST.get("studID")
            data.department = request.POST.get("department")
            data.save()
            messages.success(request, 'Successfully Updated your Personal Information.')
            return redirect('/s_profile')
        except:
            messages.error(request, 'Invalid Credentials!')
            return redirect('/s_profile')
        

def s_adding(request):
    current_user = request.user
    # Models
    req = AddingReq.objects.filter(studID=current_user.studID)
    sched = Schedule.objects.all()
    trans = TransStatus.objects.get(TransName="Add")
    if current_user.department == "Department of Industrial Technology":
        current_user.department1 = "DIT"
        subs = Subjects.objects.filter( ((Q(course=current_user.course) & Q(year__lte=current_user.year) & Q(semester=trans.semester))) | ((Q(course__icontains=current_user.department1) & Q(year__lte=current_user.year) & Q(semester=trans.semester))) | ((Q(course='DMS') & Q(year__lte=current_user.year) & Q(semester=trans.semester))) | ((Q(course='DLA') & Q(year__lte=current_user.year) & Q(semester=trans.semester)))  ) 
        sched = Schedule.objects.all()
        context = {
            'req': req,
            'current_user': current_user,
            'trans': trans,
            'subs': subs,
            'sched': sched
        }
    elif current_user.department == "Department of Industrial Education":
        current_user.department1 = "DIE"
        subs = Subjects.objects.filter( ((Q(course=current_user.course) & Q(year__lte=current_user.year) & Q(semester=trans.semester))) | ((Q(course__icontains=current_user.department1) & Q(year__lte=current_user.year) & Q(semester=trans.semester))) | ((Q(course='DMS') & Q(year__lte=current_user.year) & Q(semester=trans.semester))) | ((Q(course='DLA') & Q(year__lte=current_user.year) & Q(semester=trans.semester)))  ) 
        sched = Schedule.objects.all()
        context = {
            'req': req,
            'current_user': current_user,
            'trans': trans,
            'subs': subs,
            'sched': sched
    }
    elif current_user.department == "Department of Engineering":
        current_user.department1 = "DOE"
        subs = Subjects.objects.filter( ((Q(course=current_user.course) & Q(year__lte=current_user.year) & Q(semester=trans.semester))) | ((Q(course__icontains=current_user.department1) & Q(year__lte=current_user.year) & Q(semester=trans.semester))) | ((Q(course='DMS') & Q(year__lte=current_user.year) & Q(semester=trans.semester))) | ((Q(course='DLA') & Q(year__lte=current_user.year) & Q(semester=trans.semester)))  ) 
        sched = Schedule.objects.all()
        context = {
            'req': req,
            'current_user': current_user,
            'trans': trans,
            'subs': subs,
            'sched': sched
    }
    else:
        context = {
            'current_user': current_user,
            'sched': sched
        }

    return render(request, 'TupAssistApp/s_adding.html', context)

def upload(request):
    current_user = request.user
    if request.method == 'POST':
        data = registration.objects.get(username=current_user.username)
        data.upload = request.FILES["gradesfile"]
        data.save()
        messages.success(request, 'Successfully Upload your file.')
        return redirect('/s_adding')

def delupload(request):
    current_user = request.user
    data = registration.objects.get(username=current_user.username)
    data.upload = ""
    data.save()
    return redirect('/s_adding')

def s_add_sub(request):
    current_user = request.user
    if request.method =='POST':
        school_year = request.POST.get('school_year')
        semester = request.POST.get('semester')
        subject = request.POST.get('subject')
        section = request.POST.get('section')
        schedule = request.POST.get('schedule')
        data = AddingReq.objects.create(school_year=school_year, semester=semester, studID_id= current_user.studID, subject_id=subject, section=section, sched=schedule)
        data.save()
        messages.success(request, 'Subject Added')
        return redirect('/s_adding')

def s_del_sub(request, id):
    data = AddingReq.objects.get(id=id)
    data.delete()
    messages.success(request, 'Subject Deleted')
    return redirect('/s_adding')

def s_step1_submit(request):
    current_user = request.user
    if request.method =='POST':
        data = registration.objects.get(username=current_user.username)
        data.addStatus = 'Wait for PIC Approval'
        data.save()
        return redirect('/s_adding')
        
def s_edit_sub(request):
    if request.method =='POST':
        id = request.POST.get('id')
        data = AddingReq.objects.get(id=id)
        data.subject = request.POST.get('subject')
        data.section = request.POST.get('section')
        data.sched = request.POST.get('sched')
        data.save()
        messages.success(request, 'Update Successfuly')
        return redirect('/s_adding')


def s_step2_submit(request):
    # current_user = request.user
    # data = registration.objects.get(username=current_user.username)
    # data.addStatus = 'Updated Request'
    # data.save()
    return redirect('/s_adding')



def s_dropping(request):
    current_user = request.user
    dropReq = DroppingReq.objects.filter(studID=current_user.studID)
    trans = TransStatus.objects.get(TransName="Drop")
    sched = Schedule.objects.all()
    if current_user.department == "Department of Industrial Technology":
        current_user.department1 = "DIT"
        subs = Subjects.objects.filter( ((Q(course=current_user.course) & Q(year=current_user.year) & Q(semester=trans.semester))) | ((Q(course__icontains=current_user.department1) & Q(year=current_user.year) & Q(semester=trans.semester))) | ((Q(course='DMS') & Q(year=current_user.year) & Q(semester=trans.semester))) | ((Q(course='DLA') & Q(year=current_user.year) & Q(semester=trans.semester)))  ) 
        sched = Schedule.objects.all()
        context = {
            'dropReq': dropReq,
            'current_user': current_user,
            'trans': trans,
            'subs': subs,
            'sched': sched
    }
    elif current_user.department == "Department of Industrial Education":
        current_user.department1 = "DIE"
        subs = Subjects.objects.filter( ((Q(course=current_user.course) & Q(year=current_user.year) & Q(semester=trans.semester))) | ((Q(course__icontains=current_user.department1) & Q(year=current_user.year) & Q(semester=trans.semester))) | ((Q(course='DMS') & Q(year=current_user.year) & Q(semester=trans.semester))) | ((Q(course='DLA') & Q(year=current_user.year) & Q(semester=trans.semester)))  ) 
        sched = Schedule.objects.all()
        context = {
            'dropReq': dropReq,
            'current_user': current_user,
            'trans': trans,
            'subs': subs,
            'sched': sched
    }
    elif current_user.department == "Department of Engineering":
        current_user.department1 = "DOE"
        subs = Subjects.objects.filter( ((Q(course=current_user.course) & Q(year=current_user.year) & Q(semester=trans.semester))) | ((Q(course__icontains=current_user.department1) & Q(year=current_user.year) & Q(semester=trans.semester))) | ((Q(course='DMS') & Q(year=current_user.year) & Q(semester=trans.semester))) | ((Q(course='DLA') & Q(year=current_user.year) & Q(semester=trans.semester)))  ) 
        sched = Schedule.objects.all()
        context = {
            'dropReq': dropReq,
            'current_user': current_user,
            'trans': trans,
            'subs': subs,
            'sched': sched
    }
    else:
        context = {
            'current_user': current_user,
            'sched': sched
        }
    return render(request, 'TupAssistApp/s_dropping.html', context)

def s_drop_sub(request):
    current_user = request.user
    if request.method =='POST':
        subject1 = request.POST.get('subject1')
        subject2 = request.POST.get('subject2')
        subject3 = request.POST.get('subject3')
        subject4 = request.POST.get('subject4')
        subject5 = request.POST.get('subject5')
        subject6 = request.POST.get('subject6')
        subject7 = request.POST.get('subject7')
        subject8 = request.POST.get('subject8')
        subject9 = request.POST.get('subject9')
        subject10 = request.POST.get('subject10')
        subject11 = request.POST.get('subject11')
        subject12 = request.POST.get('subject12')

        section1 = request.POST.get('section1')
        section2 = request.POST.get('section2')
        section3 = request.POST.get('section3')
        section4 = request.POST.get('section4')
        section5 = request.POST.get('section5')
        section6 = request.POST.get('section6')
        section7 = request.POST.get('section7')
        section8 = request.POST.get('section8')
        section9 = request.POST.get('section9')
        section10 = request.POST.get('section10')
        section11 = request.POST.get('section11')
        section12 = request.POST.get('section12')

        schedule1 = request.POST.get('schedule1')
        schedule2 = request.POST.get('schedule2')
        schedule3 = request.POST.get('schedule3')
        schedule4 = request.POST.get('schedule4')
        schedule5 = request.POST.get('schedule5')
        schedule6 = request.POST.get('schedule6')
        schedule7 = request.POST.get('schedule7')
        schedule8 = request.POST.get('schedule8')
        schedule9 = request.POST.get('schedule9')
        schedule10 = request.POST.get('schedule10')
        schedule11 = request.POST.get('schedule11')
        schedule12 = request.POST.get('schedule12')

        teacher1 = request.POST.get('email1')
        teacher2 = request.POST.get('email2')
        teacher3 = request.POST.get('email3')
        teacher4 = request.POST.get('email4')
        teacher5 = request.POST.get('email5')
        teacher6 = request.POST.get('email6')
        teacher7 = request.POST.get('email7')
        teacher8 = request.POST.get('email8')
        teacher9 = request.POST.get('email9')
        teacher10 = request.POST.get('email10')
        teacher11 = request.POST.get('email11')
        teacher12 = request.POST.get('email12')

        reason = request.POST.get('reason')
        school_year = request.POST.get('school_year')
        semester = request.POST.get('semester')

        if subject1 and section1 and schedule1 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject1, section=section1, sched=schedule1, subj_teacher_name=teacher1, reason=reason, school_year=school_year, semester=semester)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
        if subject2 and section2 and schedule2 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject2, section=section2, sched=schedule2, subj_teacher_name=teacher2, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
        if subject3 and section3 and schedule3 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject3, section=section3, sched=schedule3, subj_teacher_name=teacher3, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
        if subject4 and section4 and schedule4 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject4, section=section4, sched=schedule4, subj_teacher_name=teacher4, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
        if subject5 and section5 and schedule5 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject5, section=section5, sched=schedule5, subj_teacher_name=teacher5, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
        if subject6 and section6 and schedule6 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject6, section=section6, sched=schedule6, subj_teacher_name=teacher6, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
        if subject7 and section7 and schedule7 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject7, section=section7, sched=schedule7, subj_teacher_name=teacher7, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
        if subject8 and section8 and schedule8 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject8, section=section8, sched=schedule8, subj_teacher_name=teacher8, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
        if subject9 and section9 and schedule9 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject9, section=section9, sched=schedule9, subj_teacher_name=teacher9, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
        if subject10 and section10 and schedule10 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject10, section=section10, sched=schedule10, subj_teacher_name=teacher10, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
        if subject11 and section11 and schedule11 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject11, section=section11, sched=schedule11, subj_teacher_name=teacher11, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
        if subject12 and section12 and schedule12 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject12, section=section12, sched=schedule12, subj_teacher_name=teacher12, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()

        messages.success(request, 'Subject to Drop Successfully Request Wait for the Teacher Approval.')
        return redirect('/s_dropping')



def s_transferring(request):
    current_user = request.user
    transReq = TransferringReq.objects.filter(studID_id=current_user.studID)
    trans = TransStatus.objects.get(TransName="Transfer")
    sched = Schedule.objects.all()
    if current_user.department == "Department of Industrial Technology":
        current_user.department1 = "DIT"
        subs = Subjects.objects.filter( ((Q(course=current_user.course) & Q(year=current_user.year) & Q(semester=trans.semester))) | ((Q(course__icontains=current_user.department1) & Q(year=current_user.year) & Q(semester=trans.semester))) | ((Q(course='DMS') & Q(year=current_user.year) & Q(semester=trans.semester))) | ((Q(course='DLA') & Q(year=current_user.year) & Q(semester=trans.semester)))  ) 
        sched = Schedule.objects.all()
        context = {
            'transReq': transReq,
            'current_user': current_user,
            'trans': trans,
            'subs': subs,
            'sched': sched
    }
    elif current_user.department == "Department of Industrial Education":
        current_user.department1 = "DIE"
        subs = Subjects.objects.filter( ((Q(course=current_user.course) & Q(year=current_user.year) & Q(semester=trans.semester))) | ((Q(course__icontains=current_user.department1) & Q(year=current_user.year) & Q(semester=trans.semester))) | ((Q(course='DMS') & Q(year=current_user.year) & Q(semester=trans.semester))) | ((Q(course='DLA') & Q(year=current_user.year) & Q(semester=trans.semester)))  ) 
        sched = Schedule.objects.all()
        context = {
            'transReq': transReq,
            'current_user': current_user,
            'trans': trans,
            'subs': subs,
            'sched': sched
    }
    elif current_user.department == "Department of Engineering":
        current_user.department1 = "DOE"
        subs = Subjects.objects.filter( ((Q(course=current_user.course) & Q(year=current_user.year) & Q(semester=trans.semester))) | ((Q(course__icontains=current_user.department1) & Q(year=current_user.year) & Q(semester=trans.semester))) | ((Q(course='DMS') & Q(year=current_user.year) & Q(semester=trans.semester))) | ((Q(course='DLA') & Q(year=current_user.year) & Q(semester=trans.semester)))  ) 
        sched = Schedule.objects.all()
        context = {
            'transReq': transReq,
            'current_user': current_user,
            'trans': trans,
            'subs': subs,
            'sched': sched
    }
    else:
        context = {
            'current_user': current_user,
            'sched': sched
        }
    
    return render(request, 'TupAssistApp/s_transferring.html', context)

def s_trans_sub(request):
    current_user = request.user
    if request.method =='POST':
        school_year = request.POST.get('school_year')
        semester = request.POST.get('semester')
        subject = request.POST.get('subject')
        section = request.POST.get('section')
        schedule = request.POST.get('schedule')
        data = TransferringReq.objects.create(school_year=school_year, semester=semester, studID_id= current_user.studID, subject_id=subject, section=section, sched=schedule)
        data.save()
        messages.success(request, 'Subject Tranfer Request')
        return redirect('/s_transferring')

def s_del_sub_t(request, id):
    data = TransferringReq.objects.get(id=id)
    data.delete()
    messages.success(request, 'Subject Deleted')
    return redirect('/s_transferring')

def s_step1_submit_t(request):
    current_user = request.user
    if request.method =='POST':
        data = registration.objects.get(username=current_user.username)
        data.transferStatus = 'Wait for Teacher Approval'
        data.save()
        return redirect('/s_transferring')





# PIC PAGES
def p_profile(request):
    current_user = request.user
    form = PasswordChangeForm(current_user)
    # Models
    context = {
        'current_user': current_user,
        'form': form
    }
    return render(request, 'TupAssistApp/p_profile.html', context)

def changepassword1(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Change Password Successfully')
            return redirect('/p_profile')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('/p_profile')

def changepicinfo(request):
    current_user = request.user
    if request.method == 'POST':
        try:
            data = registration.objects.get(username=current_user.username)
            data.course = request.POST.get("course")
            data.studID = request.POST.get("studID")
            data.department = request.POST.get("department")
            data.save()
            messages.success(request, 'Successfully Updated your Personal Information.')
            return redirect('/p_profile')
        except:
            messages.error(request, 'Invalid Credentials!')
            return redirect('/p_profile')


def p_adding(request):
    current_user = request.user
    test = registration.objects.filter(Q(course=current_user.course) & Q(userType='Student') & ~Q(addStatus=''))
    context = { 
        'test': test,
        'current_user': current_user
        }
    return render(request, 'TupAssistApp/p_adding.html', context )

def p_adding_edit(request, studID):
    current_user = request.user
    student_info = registration.objects.get(studID=studID)
    req = AddingReq.objects.filter(studID_id=student_info.studID)
    sched = Schedule.objects.all()
    trans = TransStatus.objects.get(TransName="Add")
    if student_info.department == "Department of Industrial Technology":
        student_info.department1 = "DIT"
        subs = Subjects.objects.filter( ((Q(course=student_info.course) & Q(year__lte=student_info.year) & Q(semester=trans.semester))) | ((Q(course__icontains=student_info.department1) & Q(year__lte=student_info.year) & Q(semester=trans.semester))) | ((Q(course='DMS') & Q(year__lte=student_info.year) & Q(semester=trans.semester))) | ((Q(course='DLA') & Q(year__lte=student_info.year) & Q(semester=trans.semester)))  ) 
        sched = Schedule.objects.all()
        context = {
            'current_user': current_user,
            'student_info': student_info,
            'req': req,
            'sched': sched,
            'subs': subs,
 
        }
    elif student_info.department == "Department of Industrial Education":
        student_info.department1 = "DIE"
        subs = Subjects.objects.filter( ((Q(course=student_info.course) & Q(year__lte=student_info.year) & Q(semester=trans.semester))) | ((Q(course__icontains=student_info.department1) & Q(year__lte=student_info.year) & Q(semester=trans.semester))) | ((Q(course='DMS') & Q(year__lte=student_info.year) & Q(semester=trans.semester))) | ((Q(course='DLA') & Q(year__lte=student_info.year) & Q(semester=trans.semester)))  ) 
        sched = Schedule.objects.all()
        context = {
            'current_user': current_user,
            'student_info': student_info,
            'req': req,
            'sched': sched,
            'subs': subs,
 
        }
    elif student_info.department == "Department of Engineering":
        student_info.department1 = "DOE"
        subs = Subjects.objects.filter( ((Q(course=student_info.course) & Q(year__lte=student_info.year) & Q(semester=trans.semester))) | ((Q(course__icontains=student_info.department1) & Q(year__lte=student_info.year) & Q(semester=trans.semester))) | ((Q(course='DMS') & Q(year__lte=student_info.year) & Q(semester=trans.semester))) | ((Q(course='DLA') & Q(year__lte=student_info.year) & Q(semester=trans.semester)))  ) 
        sched = Schedule.objects.all()
        context = {
            'current_user': current_user,
            'student_info': student_info,
            'req': req,
            'sched': sched,
            'subs': subs,
 
        }
    else:
        context = {
            'current_user': current_user,
            'student_info': student_info,
            'req': req,
            'sched': sched
        }

    return render(request, 'TupAssistApp/p_adding_edit.html', context)

def p_edit_sub(request):
    studID = request.POST.get('studID')
    data = registration.objects.get(studID=studID)
    if request.method =='POST':
        id = request.POST.get('id')   
        edit = AddingReq.objects.get(id=id)
        edit.section = request.POST.get('section')
        edit.sched = request.POST.get('sched')
        edit.pic_is_approve = request.POST.get('pic_is_approve')
        edit.pic_remark = request.POST.get('pic_remark')
        edit.pic_name = request.POST.get('pic_name')
        edit.pic_date = datetime.now()
        edit.save()
        messages.success(request, 'Request Successfully Edited!')
        return redirect('/p_adding_edit/'+ str(data.studID))

def p_add_sub(request):
    studID = request.POST.get('studID')
    data = registration.objects.get(studID=studID)
    if request.method =='POST':
        school_year = request.POST.get('school_year')
        semester = request.POST.get('semester')   
        studID = request.POST.get('studID')
        subject = request.POST.get('subject')
        section = request.POST.get('section')
        sched = request.POST.get('sched')
        pic_is_approve = request.POST.get('pic_is_approve')
        pic_remark = request.POST.get('pic_remark')
        pic_name = request.POST.get('pic_name')
        pic_date = datetime.now()
        add = AddingReq.objects.create(school_year=school_year, semester=semester, studID_id=studID, subject=subject, section=section, sched=sched, pic_is_approve=pic_is_approve, pic_remark=pic_remark, pic_name=pic_name, pic_date=pic_date)
        add.save()
        messages.success(request, 'Subject Successfully Add!')
        return redirect('/p_adding_edit/'+ str(data.studID))

def p_step1_submit(request):
    studID = request.POST.get('studID')
    if request.method =='POST':
        data = registration.objects.get(studID=studID)
        data.addStatus = 'Wait for Department Head and Asst. Director for Academic Affairs Approval'
        data.save()
        return redirect('/p_adding_edit/'+ str(data.studID))

def p_requests(request):
    current_user = request.user
    req = DroppingReq.objects.filter(subj_teacher_name=current_user.email)
    context = {
        'current_user': current_user,
        'req': req,
    }
    return render(request, 'TupAssistApp/p_requests.html', context)

def p_edit_sub(request):
    if request.method =='POST':
        id = request.POST.get('id')   
        edit = DroppingReq.objects.get(id=id)
        edit.section = request.POST.get('section')
        edit.sched = request.POST.get('sched')
        edit.subj_teacher_approve = request.POST.get('subj_teacher_approve')
        edit.subj_teacher_remark = request.POST.get('subj_teacher_remark')
        edit.subj_teacher_name = request.POST.get('subj_teacher_name')
        edit.subj_teacher_date = datetime.now()
        edit.save()
        messages.success(request, 'Request Successfully Edited!')
        return redirect('/p_requests')
        

#  TEACHER PAGES
def t_profile(request):
    current_user = request.user
    form = PasswordChangeForm(current_user)
    context = {
        'current_user': current_user,
        'form': form
    }
    return render(request, 'TupAssistApp/t_profile.html', context)

def t_requests(request):
    current_user = request.user
    req = DroppingReq.objects.filter(subj_teacher_name=current_user.email)
    context = {
        'current_user': current_user,
        'req': req,
    }
    return render(request, 'TupAssistApp/t_requests.html', context)

def t_edit_sub(request):
    if request.method =='POST':
        id = request.POST.get('id')   
        edit = DroppingReq.objects.get(id=id)
        edit.section = request.POST.get('section')
        edit.sched = request.POST.get('sched')
        edit.subj_teacher_approve = request.POST.get('subj_teacher_approve')
        edit.subj_teacher_remark = request.POST.get('subj_teacher_remark')
        edit.subj_teacher_name = request.POST.get('subj_teacher_name')
        edit.subj_teacher_date = datetime.now()
        edit.save()
        messages.success(request, 'Request Successfully Edited!')
        return redirect('/t_requests')





# DEPARTMENT HEAD PAGES

def h_profile(request):
    current_user = request.user
    form = PasswordChangeForm(current_user)
    # Models
    context = {
        'current_user': current_user,
        'form': form
    }
    return render(request, 'TupAssistApp/h_profile.html', context)

def changepassword2(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Change Password Successfully')
            return redirect('/h_profile')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('/h_profile')

def changeheadinfo(request):
    current_user = request.user
    if request.method == 'POST':
        try:
            data = registration.objects.get(username=current_user.username)
            data.studID = request.POST.get("studID")
            data.department = request.POST.get("department")
            data.save()
            messages.success(request, 'Successfully Updated your Personal Information.')
            return redirect('/h_profile')
        except:
            messages.error(request, 'Invalid Credentials!')
            return redirect('/h_profile')

def h_subject(request):
    current_user = request.user
    if current_user.department == "Department of Industrial Technology":
        current_user.department1 = "DIT"
        current_user.department2 = "BET"
        subs = Subjects.objects.filter (Q(course__icontains=current_user.department1) | Q(course__icontains=current_user.department2) ) 
        context = {
            'current_user': current_user,
            'subs': subs,
    }
    elif current_user.department == "Department of Math and Science":
        current_user.department1 = "DMS"
        subs = Subjects.objects.filter (Q(course__icontains=current_user.department1)) 
        context = {
            'current_user': current_user,
            'subs': subs,
    }
    elif current_user.department == "Department of Liberal Arts":
        current_user.department1 = "DLA"
        subs = Subjects.objects.filter (Q(course__icontains=current_user.department1)) 
        context = {
            'current_user': current_user,
            'subs': subs,
    }
    return render(request, 'TupAssistApp/h_subject.html', context)

def sub_cvs(request):
    if request.method=='POST': 
        # junk = Subjects.objects.all()
        # junk.delete()
        subcvsfile = request.FILES["subcvsfile"]
        decoded_file = subcvsfile.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)
        print(reader)
        for row in reader:
            print(row)
            try:
                if str(row[4]) == "" or str(row[4]) != "":
                    new_revo = Subjects.objects.create(subject=str(row[0])+str(row[1])+str(row[2])+str(row[3])+str(row[4]), course=str(row[0]), year=int(row[1]), semester=int(row[2]), shop=int(row[3]), is_lab=str(row[4]), description=str(row[5]))
                    new_revo.save()
            except:
                messages.success(request, 'Successfully Import, but check if data imported is correct.')
                return redirect('/h_subject')
        return redirect('/h_subject')
    return redirect('/h_subject')


def h_adding(request):
    current_user = request.user
    if current_user.department == "Department of Industrial Technology" or current_user.department == "Department of Engineering" or current_user.department == "Department of Information Education":
        test = registration.objects.filter(Q(department=current_user.department) & Q(userType='Student') & Q(addStatus='Wait for Department Head and Asst. Director for Academic Affairs Approval'))
        context = { 
            'test': test,
            'current_user': current_user
            }
    else:
        test = registration.objects.filter(userType='Student')
        context = { 
            'test': test,
            'current_user': current_user
            }
    return render(request, 'TupAssistApp/h-adding.html', context)

def h_adding_edit(request, studID):
    current_user = request.user
    data = registration.objects.get(studID=studID)
    req = AddingReq.objects.filter(studID_id=data.studID)
    sched = Schedule.objects.all()
    context = { 
        'current_user': current_user,
        'student_info': data,
        'req': req,
        'sched': sched
        }
    return render(request, 'TupAssistApp/h-adding-edit.html', context)

def h_edit_sub(request):
    studID = request.POST.get('studID')
    data = registration.objects.get(studID=studID)
    if request.method =='POST':
        id = request.POST.get('id')   
        edit = AddingReq.objects.get(id=id) 
        edit.head_is_approve = request.POST.get('head_is_approve')
        edit.head_remark = request.POST.get('head_remark')
        edit.head_name = request.POST.get('head_name')
        edit.head_date = datetime.now()
        edit.save()
        messages.success(request, 'Request Successfully Edited!')
        return redirect('/h_adding_edit/'+ str(data.studID))
        
def h_dropping(request):
    current_user = request.user
    if current_user.department == "Department of Industrial Technology" or current_user.department == "Department of Engineering" or current_user.department == "Department of Information Education":
        test = registration.objects.filter(Q(department=current_user.department) & Q(userType='Student') & Q(dropStatus='Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'))
        context = { 
            'test': test,
            'current_user': current_user
            }
    else:
        test = registration.objects.filter(userType='Student')
        context = { 
            'test': test,
            'current_user': current_user
            }
    return render(request, 'TupAssistApp/h-dropping.html', context)

def h_dropping_edit(request, studID):
    current_user = request.user
    data = registration.objects.get(studID=studID)
    req = DroppingReq.objects.filter(studID_id=data.studID)
    sched = Schedule.objects.all()
    context = { 
        'current_user': current_user,
        'student_info': data,
        'req': req,
        'sched': sched
        }
    return render(request, 'TupAssistApp/h_dropping_edit.html', context)

def h_edit_sub1(request):
    studID = request.POST.get('studID')
    data = registration.objects.get(studID=studID)
    if request.method =='POST':
        id = request.POST.get('id')   
        edit = DroppingReq.objects.get(id=id) 
        edit.subj_teacher_approve = request.POST.get('subj_teacher_approve')
        edit.subj_teacher_remark = request.POST.get('subj_teacher_remark')
        edit.subj_teacher_name = request.POST.get('subj_teacher_name')
        edit.head_is_approve = request.POST.get('head_is_approve')
        edit.head_remark = request.POST.get('head_remark')
        edit.head_name = request.POST.get('head_name')
        edit.head_date = datetime.now()
        edit.save()
        messages.success(request, 'Request Successfully Edited!')
        return redirect('/h_dropping_edit/'+ str(data.studID))
 

def h_transferring(request):
    current_user = request.user
    if current_user.department == "Department of Industrial Technology" or current_user.department == "Department of Engineering" or current_user.department == "Department of Information Education":
        test = registration.objects.filter(Q(department=current_user.department) & Q(userType='Student') & Q(transferStatus='Wait for Teacher, Department Head and Asst. Director for Academic Affairs Approval'))
        context = { 
            'test': test,
            'current_user': current_user
            }
    else:
        test = registration.objects.filter(userType='Student')
        context = { 
            'test': test,
            'current_user': current_user
            }
    return render(request, 'TupAssistApp/h-transferring.html', context)

def h_transferring_edit(request, studID):
    current_user = request.user
    data = registration.objects.get(studID=studID)
    req = TransferringReq.objects.filter(studID_id=data.studID)
    sched = Schedule.objects.all()
    context = { 
        'current_user': current_user,
        'student_info': data,
        'req': req,
        'sched': sched
        }
    return render(request, 'TupAssistApp/h-transferring-edit.html', context)
