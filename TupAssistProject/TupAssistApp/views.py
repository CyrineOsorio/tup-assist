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
        print(password)
        user = authenticate(request, username=username, password=password) 
        print(user)

        if user is not None and user.is_superuser == True:
            login(request, user)
            return redirect('/r_dashboard')

        elif user is not None and user.userType == 'Student':
            login(request, user)
            return redirect('/s_profile')
        
        elif user is not None and user.userType == 'Department Head':
            login(request, user)
            return redirect('/h-adding')

        elif user is not None and user.userType == 'Person-in-charge':
            login(request, user)
            return redirect('/p_adding')
        else:
           messages.error(request, 'Invalid Credentials')
    return render(request, 'TupAssistApp/index.html')


#LOG OUT
def logoutUser(request):
    logout(request)
    return redirect('/index')

# CUSTOMIZE ADMIN PAGES FOR OAA AND REGISTRAR

def r_dashboard(request):
    current_user = request.user
    subs = Subjects.objects.all()
    status = TransStatus.objects.all()
    sched = Schedule.objects.all()
    student = registration.objects.filter(userType='STDNT')
    # latest_sched = sched.gSheetLink
    # print(latest_sched)
    context = {
        'current_user': current_user,
        'subs': subs,
        'status' : status,
        'sched': sched,
        'student': student
    }
    return render(request, 'TupAssistApp/r_dashboard.html', context)

def sub_cvs(request):
    if request.method=='POST': 
        junk = Subjects.objects.all()
        junk.delete()
        subcvsfile = request.FILES["subcvsfile"]
        decoded_file = subcvsfile.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)
        print(reader)
        for row in reader:
            print(row)
            try:
                new_revo = Subjects.objects.create(program=str(row[0]), school_year=int(row[1]), semester=str(row[2]), subject_code=str(row[3]), description=str(row[4]))
                new_revo.save()
            except:
                messages.error(request, 'it looks like CSV format is not match to the table.')
                return redirect('/r_dashboard')
        return redirect('/r_dashboard')
    return redirect('/r_dashboard')


def import_sched(request):
    if request.method=='POST': 
        gSheetLink = request.POST.get('gSheetLink')
        school_year = request.POST.get('school_year')
        semester = request.POST.get('semester')
        course_year_and_section  = request.POST.get('course_year_and_section')
        slots  = request.POST.get('slots')
        data = Schedule.objects.create(gSheetLink = gSheetLink, school_year = school_year, semester = semester, course_year_and_section=course_year_and_section, slots=slots)
        data.save()
        return redirect('/r_dashboard')

# switch toggle for transaction status
# https://stackoverflow.com/questions/55671266/how-to-use-toggle-switch-with-django-boolean-field

def transStatus(request,id):
    status = TransStatus.objects.get(id=id)
    print(status)
    if status.status == 'Open':
        status1 = 'Close'
        status.status = status1
        status.save()
        print(status)
        return redirect('/r_dashboard')
    else:
        status.status = 'Open'
        status.save()
        return redirect('/r_dashboard')

def r_adding(request):
    current_user = request.user = request.user
    test = registration.objects.filter(userType='STDNT')
    context = { 
        'test': test,
        'current_user': current_user,
        }
    return render(request, 'TupAssistApp/r_adding.html', context)

def r_adding_view(request, id):
    current_user = request.user
    data = registration.objects.get(id=id)
    req = AddingReq.objects.filter(studID=data.studID)
    context = { 
        'req': req,
        'current_user': current_user
        }
    return render(request, 'TupAssistApp/r_adding_view.html', context)

def r_dropping(request):
    current_user = request.user
    test = registration.objects.filter(userType='STDNT')
    context = {
        'test': test,
        'current_user': current_user
        }
    return render(request, 'TupAssistApp/r_dropping.html', context)

def r_transferring(request):
    current_user = request.user
    test = registration.objects.filter(userType='STDNT')
    context = { 
        'test': test,
        'current_user': current_user
        }
    return render(request, 'TupAssistApp/r_transferring.html', context)


def r_account(request):
    current_user = request.user
    form = HeadRegistration()
    staff = registration.objects.filter(Q(userType='Department Head') | Q(userType='Program-in-Charge'))
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
            return redirect ('/admin')
        else:
            messages.error(request, 'Invalid Credentials!')
    return render(request, 'TupAssistApp/r_account.html', context)


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
                new_revo = registration.objects.create(username=str(row[2]), email=str(row[2]), first_name=str(row[0]), last_name=str(row[1]), userType='Student')
                new_revo.set_password('TUPC-'+str(row[0])+str(row[1])) #Default Password
                new_revo.save()    
                messages.success(request, 'Successfully Import, but check if data imported is correct.')
            except:
                messages.error(request, 'it looks like CSV format is not match to the table.')
                return redirect('/r_account')
        return redirect('/r_account')
    return redirect('/r_account')


def staff_acc_cvs(request):
    if request.method=='POST':
        junk = registration.objects.all(Q(userType='Department Head') | Q(userType='Program-in-Charge'))
        junk.delete()
        form = StudentRegistration(request.POST)
        staffcvsfile = request.FILES["staffcvsfile"]
        decoded_file = staffcvsfile.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)
        print(reader)
        for row in reader:
            try:
                new_revo = registration.objects.create(username=str(row[2]), email=str(row[2]), first_name=str(row[0]), last_name=str(row[1]), userType=str(row[4]))
                new_revo.set_password('TUPC-'+str(row[3])) #Default Password
                new_revo.save()    
                messages.success(request, 'Successfully Import, but check if data imported is correct.')
            except:
                messages.error(request, 'it looks like CSV format is not match to the table.')
                return redirect('/r_account')
        return redirect('/r_account')
    return redirect('/r_account')


def r_staff_create(request):
    form = HeadRegistration(request.POST)
    if form.is_valid():
        form.save()
        messages.error(request, 'Account Successfully Created!')
        return redirect ('/r_staff')
    else:
        messages.error(request, 'Invalid Credentials!')
        return redirect ('/r_staff')
    return render(request, 'TupAssistApp/r_staff.html')



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
    sub = Subjects.objects.all()
    sched = Schedule.objects.all()
    context = {
        'req': req,
        'current_user': current_user,
        'sub': sub,
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
        subject = request.POST.get('subject')
        section = request.POST.get('section')
        schedule = request.POST.get('schedule')
        data = AddingReq.objects.create(studID= current_user.studID, subject=subject, section=section, sched=schedule)
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
        mon_start = request.POST.get('mon_start')
        mon_end = request.POST.get('mon_end')
        tue_start = request.POST.get('tue_start')
        tue_end = request.POST.get('tue_end')
        wed_start = request.POST.get('wed_start')
        wed_end = request.POST.get('wed_end')
        thu_start = request.POST.get('thu_start')
        thu_end = request.POST.get('thu_end')
        fri_start = request.POST.get('fri_start')
        fri_end = request.POST.get('fri_end')
        sat_start = request.POST.get('sat_start')
        sat_end = request.POST.get('sat_end')
        print('something')
       
        print(sat_end.strftime("%I:%M %p"))
        return redirect('/s_adding')

        # if ( mon_start and mon_end != '') or ( tue_start and tue_end != '') or ( wed_start and wed_end != '') or ( thu_start and thu_end != '') or ( fri_start and fri_end != '') or ( sat_start and sat_end != ''):
        #         data1= AddingReq.objects.get(id=id)
        #         data1.id = request.POST.get('id')
        #         data1.section = request.POST.get('section')
        #         data1.sched = M + ' ' + mon_start + '-' + mon_end + ' ' + T + ' ' + tue_start + '-' + tue_end + ' ' + W + ' ' + wed_start + '-' + wed_start + ' ' + TH + ' ' + thu_start + '-' + thu_end + ' ' + F + ' ' + fri_start + '-' + fri_end + ' ' + S + ' ' + sat_start + '-' + sat_end
        #         data1.save()
        #         return redirect('/s_adding')
        # else:
        #     messages.error(request, 'Must Input atleast 1 sched')
        #     return redirect('/s_adding')


def s_step2_submit(request):
    current_user = request.user
    data = registration.objects.get(username=current_user.username)
    data.addStatus = 'Wait for Department Head Approval'
    data.save()
    return redirect('/s_adding')



def s_dropping(request):
    current_user = request.user
    # Models
    dropReq = DroppingReq.objects.filter(studID=current_user.studID)
    sub = Subjects.objects.all()
    sched = Schedule.objects.all()

    context = {
        'dropReq': dropReq,
        'current_user': current_user,
        'sub': sub,
        'sched': sched

    }
    return render(request, 'TupAssistApp/s_dropping.html', context)




def s_transferring(request):
    current_user = request.user
    # Models
    transReq = TransferringReq.objects.filter(studID=current_user.studID)
    sub = Subjects.objects.all()
    sched = Schedule.objects.all()

    context = {
        'transReq': transReq,
        'current_user': current_user,
        'sub': sub,
        'sched': sched

    }
    return render(request, 'TupAssistApp/s_transferring.html', context)





# PIC PAGES
def p_adding(request):
    current_user = request.user
    test = registration.objects.filter(Q(course=current_user.course) & Q(userType='STDNT'))
    context = { 
        'test': test,
        'current_user': current_user
        }
    return render(request, 'TupAssistApp/p_adding.html', context )


def p_adding_edit(request, id):
    current_user = request.user
    data = registration.objects.get(id=id)
    req = AddingReq.objects.filter(studID=data.studID)
    sched = Schedule.objects.all()
    context = { 
        'current_user': current_user,
        'student_info': data,
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
        edit.subject = request.POST.get('subject')
        edit.section = request.POST.get('section')
        edit.sched = request.POST.get('sched')
        edit.pic_is_approve = request.POST.get('pic_is_approve')
        edit.pic_remark = request.POST.get('pic_remark')
        edit.pic_name = request.POST.get('pic_name')
        edit.pic_date = datetime.now()
        edit.save()
        messages.success(request, 'Request Successfully Edited!')
        return redirect('/p_adding_edit/'+ str(data.id))

def p_step1_submit(request):
    studID = request.POST.get('studID')
    if request.method =='POST':
        data = registration.objects.get(studID=studID)
        data.addStatus = 'Wait for Department Head Approval'
        data.save()
        return redirect('/p_adding_edit/'+ str(data.id))
        



# DEPARTMENT HEAD PAGES

def h_adding(request):
    current_user = request.user
    test = registration.objects.filter(Q(department=current_user.department) & Q(userType='STDNT'))
    context = { 
        'test': test,
        'current_user': current_user
        }
    return render(request, 'TupAssistApp/h-adding.html', context)

def h_adding_edit(request, id):
    current_user = request.user
    data = registration.objects.get(id=id)
    req = AddingReq.objects.filter(studID=data.studID)
    sched = Schedule.objects.all()
    context = { 
        'current_user': current_user,
        'student_info': data,
        'req': req,
        'sched': sched
        }
    
    return render(request, 'TupAssistApp/h-adding-edit.html', context)

def h_dropping(request):
    current_user = request.user
    test = registration.objects.filter(Q(department=current_user.department) & Q(userType='STDNT'))
    context = { 
        'test': test,
        'current_user': current_user
        }
    return render(request, 'TupAssistApp/h-dropping.html', context)


def h_dropping_edit(request, id):
    current_user = request.user
    data = registration.objects.get(id=id)
    req = DroppingReq.objects.filter(studID=data.studID)
    sched = Schedule.objects.all()
    context = { 
        'current_user': current_user,
        'student_info': data,
        'req': req,
        'sched': sched
        }
    return render(request, 'TupAssistApp/h-dropping-edit.html', context)


def h_transferring(request):
    current_user = request.user
    test = registration.objects.filter(Q(department=current_user.department) & Q(userType='STDNT'))
    context = { 
        'test': test,
        'current_user': current_user
        }
    return render(request, 'TupAssistApp/h-transferring.html', context)


def h_transferring_edit(request, id):
    current_user = request.user
    data = registration.objects.get(id=id)
    req = TransferringReq.objects.filter(studID=data.studID)
    sched = Schedule.objects.all()
    context = { 
        'current_user': current_user,
        'student_info': data,
        'req': req,
        'sched': sched
        }
    return render(request, 'TupAssistApp/h-transferring-edit.html', context)


def h_schedule(request):
    current_user = request.user
    context = { 
        'current_user': current_user
        }
    return render(request, 'TupAssistApp/h-schedule.html', context)

