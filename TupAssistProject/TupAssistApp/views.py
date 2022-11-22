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
        for row in reader:
            # new_revo = StudentReference.objects.create(email=str(i)[2:-2])
            try:
                new_revo = StudentReference.objects.create(name=str(row[0]), course_year_and_section=str(row[1]), email=str(row[2]))
                new_revo.save()
            except:
                messages.error(request, 'it looks like CSV format is not match to the table.')
                return redirect('/r_dashboard')
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
        messages.error(request, 'Account Successfully Created!')
        return redirect ('/r_staff')
    else:
        messages.error(request, 'Invalid Credentials!')
        return redirect ('/r_staff')
    return render(request, 'TupAssistApp/r_staff.html')



#STUDENT PAGES

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
    data.addStatus = ''
    data.save()
    return redirect('/s_adding')

def s_step1_submit(request):
    current_user = request.user
    if request.method=='POST':
        studID = request.POST.get('studID')

        sub1 = request.POST.get('sub1')
        sub2 = request.POST.get('sub2')
        sub3 = request.POST.get('sub3')
        sub4 = request.POST.get('sub4')
        sub5 = request.POST.get('sub5')
        sub6 = request.POST.get('sub6')
        sub7 = request.POST.get('sub7')
        sub8 = request.POST.get('sub8')
        sub9 = request.POST.get('sub9')
        sub10 = request.POST.get('sub10')

        sec1 = request.POST.get('sec1')
        sec2 = request.POST.get('sec2')
        sec3 = request.POST.get('sec3')
        sec4 = request.POST.get('sec4')
        sec5 = request.POST.get('sec5')
        sec6 = request.POST.get('sec6')
        sec7 = request.POST.get('sec7')
        sec8 = request.POST.get('sec8')
        sec9 = request.POST.get('sec9')
        sec10 = request.POST.get('sec10')

        grade = current_user.upload

        # HANDLING ERROR
        if  (grade == ''):
            messages.error(request, 'Upload File first')
            return redirect('/s_adding')
        elif (sub1 == '' and sec1 == '') and (sub2 == ''and sec2  == '') and (sub3 == '' and sec3 == '') and (sub4 == '' and sec4 == '') and (sub5 == '' and sec5 == '') and (sub6 == '' and sec6 == '') and (sub7 == '' and sec7 == '') and (sub8 == '' and sec8 == '') and (sub9 == '' and sec9 == '') and (sub10 == '' and sec10 == ''):
            messages.error(request, 'Input atleast 1 offer subject.') 
            return redirect('/s_adding')
        elif (sub1 != '' and sec1 != '') and (sub2 == '' and sec2 == '') and (sub3 == '' and sec3 == '') and (sub4 == '' and sec4 == '') and (sub5 == '' and sec5 == '') and (sub6 == '' and sec6 == '') and (sub7 == '' and sec7 == '') and (sub8 == '' and sec8 == '') and (sub9 == '' and sec9 == '') and (sub10 == '' and sec10 == ''):
            sub1 = AddingReq.objects.create(studID=studID, subject=sub1, section=sec1)
            sub1.save()
            data = registration.objects.get(username=current_user.username)
            data.addStatus = 'Requested: Subject to be taken is submitted.'
            data.save()
            return redirect('/s_adding')
        elif (sub1 != '' and sec1 != '') and (sub2 != '' and sec2 != '') and (sub3 == '' and sec3 == '') and (sub4 == '' and sec4 == '') and (sub5 == '' and sec5 == '') and (sub6 == '' and sec6 == '') and (sub7 == '' and sec7 == '') and (sub8 == '' and sec8 == '') and (sub9 == '' and sec9 == '') and (sub10 == '' and sec10 == ''):
            add = AddingReq.objects.bulk_create([AddingReq(studID=studID, subject=sub1, section=sec1), AddingReq(studID=studID, subject=sub2, section=sec2)])
            data = registration.objects.get(username=current_user.username)
            data.addStatus = 'Requested: Subject to be taken is submitted.'
            data.save()
            return redirect('/s_adding')
        elif (sub1 != '' and sec1 != '') and (sub2 != '' and sec2 != '') and (sub3 != '' and sec3 != '') and (sub4 == '' and sec4 == '') and (sub5 == '' and sec5 == '') and (sub6 == '' and sec6 == '') and (sub7 == '' and sec7 == '') and (sub8 == '' and sec8 == '') and (sub9 == '' and sec9 == '') and (sub10 == '' and sec10 == ''):
            add = AddingReq.objects.bulk_create([AddingReq(studID=studID, subject=sub1, section=sec1), AddingReq(studID=studID, subject=sub2, section=sec2), AddingReq(studID=studID, subject=sub3, section=sec3)])
            data = registration.objects.get(username=current_user.username)
            data.addStatus = 'Requested: Subject to be taken is submitted.'
            data.save()
            return redirect('/s_adding')
        elif (sub1 != '' and sec1 != '') and (sub2 != '' and sec2 != '') and (sub3 != '' and sec3 != '') and (sub4 != '' and sec4 != '') and (sub5 == '' and sec5 == '') and (sub6 == '' and sec6 == '') and (sub7 == '' and sec7 == '') and (sub8 == '' and sec8 == '') and (sub9 == '' and sec9 == '') and (sub10 == '' and sec10 == ''):
            add = AddingReq.objects.bulk_create([AddingReq(studID=studID, subject=sub1, section=sec1), AddingReq(studID=studID, subject=sub2, section=sec2), AddingReq(studID=studID, subject=sub3, section=sec3),
            AddingReq(studID=studID, subject=sub4, section=sec4)])
            data = registration.objects.get(username=current_user.username)
            data.addStatus = 'Requested: Subject to be taken is submitted.'
            data.save()
            return redirect('/s_adding')
        elif (sub1 != '' and sec1 != '') and (sub2 != '' and sec2 != '') and (sub3 != '' and sec3 != '') and (sub4 != '' and sec4 != '') and (sub5 != '' and sec5 != '') and (sub6 == '' and sec6 == '') and (sub7 == '' and sec7 == '') and (sub8 == '' and sec8 == '') and (sub9 == '' and sec9 == '') and (sub10 == '' and sec10 == ''):
            add = AddingReq.objects.bulk_create([AddingReq(studID=studID, subject=sub1, section=sec1), AddingReq(studID=studID, subject=sub2, section=sec2), AddingReq(studID=studID, subject=sub3, section=sec3),
            AddingReq(studID=studID, subject=sub4, section=sec4), AddingReq(studID=studID, subject=sub5, section=sec5)])
            data = registration.objects.get(studID=studID)
            data = registration.objects.get(username=current_user.username)
            data.addStatus = 'Requested: Subject to be taken is submitted.'
            data.save()
            return redirect('/s_adding')
        elif (sub1 != '' and sec1 != '') and (sub2 != '' and sec2 != '') and (sub3 != '' and sec3 != '') and (sub4 != '' and sec4 != '') and (sub5 != '' and sec5 != '') and (sub6 != '' and sec6 != '') and (sub7 == '' and sec7 == '') and (sub8 == '' and sec8 == '') and (sub9 == '' and sec9 == '') and (sub10 == '' and sec10 == ''):
            add = AddingReq.objects.bulk_create([AddingReq(studID=studID, subject=sub1, section=sec1), AddingReq(studID=studID, subject=sub2, section=sec2), AddingReq(studID=studID, subject=sub3 , section=sec3),
            AddingReq(studID=studID, subject=sub4, section=sec4), AddingReq(studID=studID, subject=sub5, section=sec5), AddingReq(studID=studID, subject=sub6, section=sec6)])
            data = registration.objects.get(username=current_user.username)
            data.addStatus = 'Requested: Subject to be taken is submitted.'
            data.save()
            return redirect('/s_adding')
        elif (sub1 != '' and sec1 != '') and (sub2 != '' and sec2 != '') and (sub3 != '' and sec3 != '') and (sub4 != '' and sec4 != '') and (sub5 != '' and sec5 != '') and (sub6 != '' and sec6 != '') and (sub7 != '' and sec7 != '') and (sub8 == '' and sec8 == '') and (sub9 == '' and sec9 == '') and (sub10 == '' and sec10 == ''):
            add = AddingReq.objects.bulk_create([AddingReq(studID=studID, subject=sub1, section=sec1), AddingReq(studID=studID, subject=sub2, section=sec2), AddingReq(studID=studID, subject=sub3, section=sec3),
            AddingReq(studID=studID, subject=sub4, section=sec4), AddingReq(studID=studID, subject=sub5, section=sec5), AddingReq(studID=studID, subject=sub6, section=sec6), AddingReq(studID=studID, subject=sub7, section=sec7)])
            data = registration.objects.get(username=current_user.username)
            data.addStatus = 'Requested: Subject to be taken is submitted.'
            data.save()
            return redirect('/s_adding')
        elif (sub1 != '' and sec1 != '') and (sub2 != '' and sec2 != '') and (sub3 != '' and sec3 != '') and (sub4 != '' and sec4 != '') and (sub5 != '' and sec5 != '') and (sub6 != '' and sec6 != '') and (sub7 != '' and sec7 != '') and (sub8 != '' and sec8 != '') and (sub9 == '' and sec9 == '') and (sub10 == '' and sec10 == ''):
            add = AddingReq.objects.bulk_create([AddingReq(studID=studID, subject=sub1, section=sec1), AddingReq(studID=studID, subject=sub2, section=sec2), AddingReq(studID=studID, subject=sub3, section=sec3),
            AddingReq(studID=studID, subject=sub4, section=sec4), AddingReq(studID=studID, subject=sub5, section=sec5), AddingReq(studID=studID, subject=sub6, section=sec6), AddingReq(studID=studID, subject=sub7, section=sec7),
            AddingReq(studID=studID, subject=sub8)])
            data = registration.objects.get(username=current_user.username)
            data.addStatus = 'Requested: Subject to be taken is submitted.'
            data.save()
            return redirect('/s_adding')
        elif (sub1 != '' and sec1 != '') and (sub2 != '' and sec2 != '') and (sub3 != '' and sec3 != '') and (sub4 != '' and sec4 != '') and (sub5 != '' and sec5 != '') and (sub6 != '' and sec6 != '') and (sub7 != '' and sec7 != '') and (sub8 != '' and sec8 != '') and (sub9 != '' and sec9 != '') and (sub10 == '' and sec10 == ''):
            add = AddingReq.objects.bulk_create([AddingReq(studID=studID, subject=sub1, section=sec1), AddingReq(studID=studID, subject=sub2, section=sec2), AddingReq(studID=studID, subject=sub3, section=sec3),
            AddingReq(studID=studID, subject=sub4, section=sec4), AddingReq(studID=studID, subject=sub5, section=sec5), AddingReq(studID=studID, subject=sub6, section=sec6), AddingReq(studID=studID, subject=sub7, section=sec7),
            AddingReq(studID=studID, subject=sub8, section=sec8),AddingReq(studID=studID, subject=sub9, section=sec9)])
            data = registration.objects.get(username=current_user.username)
            data.addStatus = 'Requested: Subject to be taken is submitted.'
            data.save()
            return redirect('/s_adding')
        elif (sub1 != '' and sec1 != '') and (sub2 != '' and sec2 != '') and (sub3 != '' and sec3 != '') and (sub4 != '' and sec4 != '') and (sub5 != '' and sec5 != '') and (sub6 != '' and sec6 != '') and (sub7 != '' and sec7 != '') and (sub8 != '' and sec8 != '') and (sub9 != '' and sec9 != '') and (sub10 != '' and sec10 != ''):
            add = AddingReq.objects.bulk_create([AddingReq(studID=studID, subject=sub1, section=sec1), AddingReq(studID=studID, subject=sub2, section=sec2), AddingReq(studID=studID, subject=sub3, section=sec3),
            AddingReq(studID=studID, subject=sub4, section=sec4), AddingReq(studID=studID, subject=sub5, section=sec5), AddingReq(studID=studID, subject=sub6, section=sec6), AddingReq(studID=studID, subject=sub7, section=sec7),
            AddingReq(studID=studID, subject=sub8, section=sec8),AddingReq(studID=studID, subject=sub9, section=sec9),AddingReq(studID=studID, subject=sub10, section=sec10)])
            data = registration.objects.get(username=current_user.username)
            data.addStatus = 'Requested: Subject to be taken is submitted.'
            data.save()
            return redirect('/s_adding')
        else:
            messages.error(request, 'Input atleast 1 offer subject or Complete the row field.')
            return redirect('/s_adding')


def s_adding_edit_sched(request):
    if request.method =='POST':
        id = request.POST.get('id')
        M = request.POST.get('M')
        T = request.POST.get('T')
        W = request.POST.get('W')
        TH = request.POST.get('TH')
        F = request.POST.get('F')
        S = request.POST.get('S')
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

        if ( mon_start and mon_end != '') or ( tue_start and tue_end != '') or ( wed_start and wed_end != '') or ( thu_start and thu_end != '') or ( fri_start and fri_end != '') or ( sat_start and sat_end != ''):
                data1= AddingReq.objects.get(id=id)
                data1.id = request.POST.get('id')
                data1.section = request.POST.get('section')
                data1.sched = M + ' ' + mon_start + '-' + mon_end + ' ' + T + ' ' + tue_start + '-' + tue_end + ' ' + W + ' ' + wed_start + '-' + wed_start + ' ' + TH + ' ' + thu_start + '-' + thu_end + ' ' + F + ' ' + fri_start + '-' + fri_end + ' ' + S + ' ' + sat_start + '-' + sat_end
                data1.save()
                return redirect('/s_adding')
        else:
            messages.error(request, 'Must Input atleast 1 sched')
            return redirect('/s_adding')


def s_step2_submit(request):
    current_user = request.user
    data = registration.objects.get(username=current_user.username)
    data.addStatus = 'Requested: Wait for PIC Approval'
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
    return render(request, 'TupAssistApp/p-adding.html', context )


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

