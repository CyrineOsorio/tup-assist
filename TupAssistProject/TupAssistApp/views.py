from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import redirect, render
#from pyexpat.errors import messages
from django.contrib import messages

from .models import *
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

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
        user = authenticate(request, username=username, password=password) 
        print(user)

        if user is not None and user.is_superuser == True:
            login(request, user)
            return redirect('/r_dashboard')

        elif user is not None and user.userType == 'STDNT':
            login(request, user)
            return redirect('/s_adding')
        
        elif user is not None and user.userType == 'DH':
            login(request, user)
            return redirect('/h-adding')

        elif user is not None and user.userType == 'Person-in-charge':
            login(request, user)
            return redirect('/p-adding')
        else:
           messages.error(request, 'Invalid Credentials')
    return render(request, 'TupAssistApp/index.html')

#STUDENT SIGN UP PAGE
def signup(request):
    form = StudentRegistration()
    if request.method == 'POST':
        form = StudentRegistration(request.POST)
        signup_data = request.POST.dict()
        email = signup_data.get("email")
        try:
            userref = StudentReference.objects.get(email=email)
            user_email = userref.email
            print(userref)
            if form.is_valid() and user_email == email:
                # Filter of Course by Department
                course = form.cleaned_data.get('course')
                print(course)
                if course == "BET-COET" or course == "BET-ET" or course == "BET-ESET" or course == "BET-CT" or course == "BET-MT" or course == "BET-AT" or course == "BET-PPT":
                    form.instance.userType = 'STDNT'
                    form.instance.department = 'Department of Industrial Technology'
                elif course == "BSCE" or course == "BSEE" or course == "BSECE" or course == "BSME":
                    form.instance.userType = 'STDNT'
                    form.instance.department = 'Department of Engineering'
                elif course == "BSIE-ICT":
                    form.instance.userType = 'STDNT'
                    form.instance.department = 'Department of Industrial Education'
                    #EDIT FOR EMAIL 5/30/2022
                    subject = 'TUP-Assist Registration'
                    message = 'Your account was already created. You have access now in add, drop and transfer subjects.'
                    recipient = form.cleaned_data.get('email')
                    send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient], fail_silently=False)
                form.save()
                return redirect ('/index')
            else:
                messages.error(request, 'Password Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.')
        except StudentReference.DoesNotExist:
            messages.error(request, 'Use Tup Cavite Gsfe Account!')
    context =  {'form': form}
    return render(request, 'TupAssistApp/student-registration.html', context)


# Head, PIC SIGN UP PAGE
def signup1(request):
    form = HeadRegistration()
    if request.method == 'POST':
        form = HeadRegistration(request.POST)
        if form.is_valid():
            form.save()
            return redirect ('/admin')
        else:
            messages.error(request, 'Invalid Credentials!')
    context =  {'form': form}
    return render(request, 'TupAssistApp/staff-registration.html', context)


#LOG OUT
def logoutUser(request):
    logout(request)
    return redirect('/index')






# PIC PAGES
def p_adding(request):
    current_user = request.user
    test = registration.objects.filter(Q(course=current_user.course) & Q(userType='STDNT'))
    context = { 
        'test': test,
        'current_user': current_user
        }
    return render(request, 'TupAssistApp/p-adding.html', context )


def p_adding_edit(request, id):
    current_user = request.user
    data = registration.objects.get(id=id)
    req = AddingReq.objects.filter(studID=data.studID)
    sched = Schedule.objects.latest('id')
    context = { 
        'current_user': current_user,
        'student_info': data,
        'req': req,
        'sched': sched
        }
    if request.method=='POST':
        ids = request.POST.get('id')
        edit = AddingReq.objects.get(id=ids)
        edit.studID = request.POST.get('studID')
        edit.subject = request.POST.get('subject')
        edit.course = request.POST.get('course')
        edit.yrandsec = request.POST.get('yrandsec')
        edit.sched = request.POST.get('sched')
        edit.picCheck = request.POST.get('picCheck')
        edit.picComment = request.POST.get('picComment')
        edit.save()
        return redirect('/p-adding-edit/'+ str(id))
    
    return render(request, 'TupAssistApp/p-adding-edit.html', context)



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
    sched = Schedule.objects.latest('id')
    context = { 
        'current_user': current_user,
        'student_info': data,
        'req': req,
        'sched': sched
        }
    if request.method=='POST':
        ids = request.POST.get('id')
        edit = AddingReq.objects.get(id=ids)
        edit.studID = request.POST.get('studID')
        edit.subject = request.POST.get('subject')
        edit.course = request.POST.get('course')
        edit.yrandsec = request.POST.get('yrandsec')
        edit.sched = request.POST.get('sched')
        edit.picCheck = request.POST.get('picCheck')
        edit.picComment = request.POST.get('picComment')
        edit.headCheck = request.POST.get('headCheck')
        edit.headComment = request.POST.get('headComment')
        edit.save()
        return redirect('/h-adding-edit/'+ str(id))
    
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
    sched = Schedule.objects.latest('id')
    context = { 
        'current_user': current_user,
        'student_info': data,
        'req': req,
        'sched': sched
        }
    if request.method=='POST':
        ids = request.POST.get('id')
        edit = DroppingReq.objects.get(id=ids)
        edit.studID = request.POST.get('studID')
        edit.subject = request.POST.get('subject')
        edit.course = request.POST.get('course')
        edit.yrandsec = request.POST.get('yrandsec')
        edit.reason = request.POST.get('reason')
        edit.headCheck = request.POST.get('headCheck')
        edit.headComment = request.POST.get('headComment')
        edit.save()
        return redirect('/h-dropping-edit/'+ str(id))
    
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
    sched = Schedule.objects.latest('id')
    context = { 
        'current_user': current_user,
        'student_info': data,
        'req': req,
        'sched': sched
        }
    if request.method=='POST':
        ids = request.POST.get('id')
        edit = TransferringReq.objects.get(id=ids)
        edit.studID = request.POST.get('studID')
        edit.subject = request.POST.get('subject')
        edit.course = request.POST.get('course')
        edit.yrandsec = request.POST.get('yrandsec')
        edit.reason = request.POST.get('reason')
        edit.headCheck = request.POST.get('headCheck')
        edit.headComment = request.POST.get('headComment')
        edit.save()
        return redirect('/h-transferring-edit/'+ str(id))
    
    return render(request, 'TupAssistApp/h-transferring-edit.html', context)




def h_schedule(request):
    current_user = request.user
    context = { 
        'current_user': current_user
        }
    return render(request, 'TupAssistApp/h-schedule.html', context)




# CUSTOMIZE ADMIN PAGES FOR OAA AND REGISTRAR

def r_dashboard(request):
    current_user = request.user
    subs = Subjects.objects.all()
    status = TransStatus.objects.all()
    sched = Schedule.objects.latest('id')
    emails = StudentReference.objects.all()
    # latest_sched = sched.gSheetLink
    # print(latest_sched)
    context = {
        'current_user': current_user,
        'subs': subs,
        'status' : status,
        'sched': sched,
        'emails': emails
    }
    return render(request, 'TupAssistApp/r_dashboard.html', context)


def acc_cvs(request):
    if request.method=='POST':
        junk = StudentReference.objects.all()
        junk.delete()
        studcvsfile = request.FILES["studcvsfile"]
        decoded_file = studcvsfile.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)
        print(reader)
        for i in reader:
            new_revo = StudentReference.objects.create(email=str(i)[2:-2])
            new_revo.save()
        return redirect('/r_dashboard')
    return redirect('/r_dashboard')

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
                new_revo = Subjects.objects.create(SubCode=str(row[0]), SubName=str(row[1]), Course=str(row[2]), Units=int(row[3]))
                new_revo.save()
            except:
                return redirect('/r_dashboard')
        return redirect('/r_dashboard')
    return redirect('/r_dashboard')


def import_sched(request):
    if request.method=='POST': 
        gSheetLink = request.POST.get('gSheetLink')
        year = request.POST.get('year')
        semester = request.POST.get('semester')
        data = Schedule.objects.create(gSheetLink = gSheetLink, year = year, semester = semester)
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
    return render(request, 'TupAssistApp/r_dashboard.html', context)

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


def r_staff(request):
    current_user = request.user
    form = HeadRegistration()
    if request.method == 'POST':
        form = HeadRegistration(request.POST)
        if form.is_valid():
            form.save()
            return redirect ('/admin')
        else:
            messages.error(request, 'Invalid Credentials!')
            
    context = { 
        'form': form,
        'current_user': current_user
        }
    return render(request, 'TupAssistApp/r_staff.html', context)



def r_staff_create(request):
    form = HeadRegistration(request.POST)
    if form.is_valid():
        form.save()
        return redirect ('/r_staff')
    else:
        messages.error(request, 'Invalid Credentials!')
    return render(request, 'TupAssistApp/r_staff.html')



#STUDENT PAGES

def s_adding(request):
    current_user = request.user
    # Models
    addReq = AddingReq.objects.filter(studID=current_user.studID)
    dropReq = DroppingReq.objects.filter(studID=current_user.studID)
    transReq = TransferringReq.objects.filter(studID=current_user.studID)
    sub = Subjects.objects.all()
    sched = Schedule.objects.latest('id')

    context = {
        'addReq': addReq,
        'dropReq': dropReq,
        'transReq': transReq,
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
        data.addStatus = 'Requested Grades Uploaded'
        data.save()
        messages.success(request, 'Successfully Upload your file. Wait for the program-in-charge, before proceeding in Step 2.')
    return redirect('/s_adding')


def delupload(request):
    current_user = request.user
    data = registration.objects.get(username=current_user.username)
    data.upload = ""
    data.addStatus = ''
    data.save()
    return redirect('/s_adding')











def s_adding1(request):
    if request.method=='POST': 
        studID = request.POST.get('studID')
        add = AddingReq.objects.create(studID=studID)
        add.save()
    return redirect('/s_adding')

def s_adding_edit(request, id):
    if request.method =='POST':
        id = request.POST.get('id')
        data1= AddingReq.objects.get(id=id)
        data1.id = request.POST.get('id')
        data1.save()
        return redirect('/s_adding')

def s_adding_del(request, id):
    data = AddingReq.objects.get(id=id)
    data.delete()
    return redirect('/s_adding')


def s_dropping(request):
    current_user = request.user
    # Models
    dropReq = DroppingReq.objects.filter(studID=current_user.studID)
    sub = Subjects.objects.all()
    sched = Schedule.objects.latest('id')

    context = {
        'dropReq': dropReq,
        'current_user': current_user,
        'sub': sub,
        'sched': sched

    }
    return render(request, 'TupAssistApp/s_dropping.html', context)



def s_dropping1(request):
    if request.method=='POST': 
        studID = request.POST.get('studID')
        add = DroppingReq.objects.create(studID=studID)
        add.save()
    return redirect('/s_dropping')

def s_dropping_del(request, id):
    data = DroppingReq.objects.get(id=id)
    data.delete()
    return redirect('/s_dropping')







def s_transferring(request):
    current_user = request.user
    # Models
    transReq = TransferringReq.objects.filter(studID=current_user.studID)
    sub = Subjects.objects.all()
    sched = Schedule.objects.latest('id')

    context = {
        'transReq': transReq,
        'current_user': current_user,
        'sub': sub,
        'sched': sched

    }
    return render(request, 'TupAssistApp/s_transferring.html', context)


def s_transferring1(request):
    if request.method=='POST': 
        studID = request.POST.get('studID')
        subject = request.POST.get('subject')
        add = TransferringReq.objects.create(studID=studID)
        add.save()
    return redirect('/s_transferring')

def s_transferring_del(request, id):
    data = TransferringReq.objects.get(id=id)
    data.delete()
    return redirect('/s_transferring')