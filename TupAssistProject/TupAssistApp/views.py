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

import easygui


# Create your views here.
installed_apps = ['TupAssistApp']



#LOGIN PAGE
def index(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password') 
        user = authenticate(request, username=username, password=password) 
        print(user)

        if user is not None and user.userType == 'STDNT':
            login(request, user)
            return redirect('/student')
        
        elif user is not None and user.userType == 'DH':
            login(request, user)
            return redirect('/head')

        elif user is not None and user.userType == 'PIC':
            login(request, user)
            return redirect('/pic')
        else:
           messages.error(request, 'Invalid Credentials')
    return render(request, 'TupAssistApp/index.html')

#SIGN UP PAGE
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
                form.save()
                messages.success(request, 'Account is successfully created!')
                return redirect ('/index')
            else:
                messages.error(request, 'Invalid Credentials!')
        except StudentReference.DoesNotExist:
            messages.error(request, 'Use Tup Cavite Gsfe Account!')
            return redirect ('/signup')
    context =  {'form': form}
    return render(request, 'TupAssistApp/signup.html', context)


def pic(request):
    return render(request, 'TupAssistApp/pic.html')

def admin(request):
    return render(request, 'TupAssistApp/admin.html')

def registrar(request):
    subs = Subjects.objects.all()
    status = TransStatus.objects.all()
    sched = Schedule.objects.latest('id')
    emails = StudentReference.objects.all()
    # latest_sched = sched.gSheetLink
    # print(latest_sched)
    context = {
        'subs': subs,
        'status' : status,
        'sched': sched,
        'emails': emails
    }
    return render(request, 'TupAssistApp/registrar.html', context)


def acc_cvs(request):
    if request.method=='POST': 
        file = easygui.fileopenbox()
        if file is not None:
            with open(file) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    new_revo = StudentReference.objects.create(email=row['Email'])
                    new_revo.save()
                return redirect('/registrar')
        else:
            messages.error(request, 'Cancelled!')
    return redirect('/registrar')


def sub_cvs(request):
    if request.method=='POST': 
        file = easygui.fileopenbox()
        print(file)
        with open(file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                new_revo = Subjects.objects.create(SubCode=row['SubCode'], SubName=row['SubName'], Course=row['Course'], Units=row['Units'])
                new_revo.save()
            return redirect('/registrar')
    return redirect('/registrar')

def import_sched(request):
    if request.method=='POST': 
        gSheetLink = request.POST.get('gSheetLink')
        year = request.POST.get('year')
        semester = request.POST.get('semester')
        data = Schedule.objects.create(gSheetLink = gSheetLink, year = year, semester = semester)
        data.save()
        return redirect('/registrar')

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
        return redirect('/registrar')
    else:
        status.status = 'Open'
        status.save()
        return redirect('/registrar')

def r_adding(request):
    return render(request, 'TupAssistApp/r-adding.html')


#STUDENT PAGE
def student(request):
    addReq = AddingReq.objects.all()
    context = {
        'addReq': addReq
    }
    return render(request, 'TupAssistApp/student.html', context)

def s_adding(request):
    if request.method=='POST': 
        subcode = request.POST.get('subcode')
        subname = request.POST.get('subname')
        course = request.POST.get('course')
        yrandsec = request.POST.get('yrandsec')
        sched = request.POST.get('sched')
        add = AddingReq.objects.create(subcode=subcode, subname=subname, course=course, yrandsec=yrandsec, sched=sched)
        add.save()
    return redirect('/student')

def s_adding_edit(request, id):
    if request.method =='POST':
        id = request.POST.get('id')
        data1= AddingReq.objects.get(id=id)
        data1.id = request.POST.get('id')
        data1.subcode = request.POST.get('subcode')
        data1.save()
        return redirect('/student')


