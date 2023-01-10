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
from django.db.models import Q, Count, Sum


# Email
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
installed_apps = ['TupAssistApp']



#LOGIN PAGE
def index(request):
    logout(request)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password) 

        if user is not None and user.is_superuser == True:
            login(request, user)
            return redirect('/a_dashboard')

        elif user is not None and user.userType == 'OAA Staff':
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
@login_required(login_url='/index')
def a_dashboard(request):
    if request.user.is_authenticated and (request.user.userType == 'OAA Staff' or request.user.is_superuser == True ):
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
    return redirect('/index')   


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
        messages.success(request, 'Successfully changed the status.')
        return redirect('/a_dashboard')


@login_required(login_url='/index')
def a_account(request):
    if request.user.is_authenticated and (request.user.userType == 'OAA Staff' or request.user.is_superuser == True ):
        current_user = request.user
        form = HeadRegistration()
        staff = registration.objects.filter(Q(userType='Department Head') | Q(userType='Program-in-Charge') | Q(userType='Teacher') | Q(userType='OAA Staff') | Q(userType='Assist. Director of Academic Affairs'))
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
                messages.error(request, 'Invalid credentials!')
        return render(request, 'TupAssistApp/a_account.html', context)
    return redirect('/index')

def student_acc_cvs(request):
    if request.method=='POST':
        # junk = registration.objects.filter(userType='Student')
        # junk.delete()
        form = StudentRegistration(request.POST)
        studcvsfile = request.FILES["studcvsfile"]
        decoded_file = studcvsfile.read().decode('utf-8').splitlines()[1:]
        reader = csv.reader(decoded_file)
        print(reader)
        for row in reader:
            try:
                new_revo = registration.objects.create(studID=str(row[0]), username=str(row[3]), email=str(row[3]), first_name=str(row[1]), last_name=str(row[2]), userType='Student')
                new_revo.set_password(str(row[0])) #Default Password
                new_revo.save()    
                messages.success(request, 'Successfully uploaded the student accounts.')
                send_mail('TUP-Assist Account', 
                "Hello " + str(row[1]) + ',\n'
                'As a student of Technological University of the Philippines - Cavite, you are automatically registered in TUP-Assist.' + '\n\n'
                'TUP-Assist is a web-based system that helps students in adding, dropping, and transferring of subjects in TUP-Cavite.' + '\n\n'
                'Attached to this are your username/email and the default password that you can change later after logging in.' + '\n\n'
                'Username/Email: ' + str(row[3]) + '\n'
                'Password: ' + str(row[0]) + '\n'
                'System Link: ' + 'https://tupassist.pythonanywhere.com' + '\n\n'
                'If there are any concerns, please reply to this email.' + '\n\n'
                'Thank you.', settings.EMAIL_HOST_USER , [str(row[3])], fail_silently=False)
            except:
                messages.error(request, 'Content of the csv does not not match to the format, or accounts are already existed create another file for the additional account.')
                return redirect('/a_account')
        return redirect('/a_account')
    return redirect('/a_account')

def staff_acc_cvs(request):
    if request.method=='POST':
        # junk = registration.objects.filter(Q(userType='Department Head') | Q(userType='Program-in-Charge') | Q(userType='Teacher') | Q(userType='OAA Staff') )
        # junk.delete()
        form = StudentRegistration(request.POST)
        staffcvsfile = request.FILES["staffcvsfile"]
        decoded_file = staffcvsfile.read().decode('utf-8').splitlines()[1:]
        reader = csv.reader(decoded_file)
        print(reader)
        for row in reader:
            try:
                new_revo = registration.objects.create(studID=str(row[0]), username=str(row[3]), email=str(row[3]), first_name=str(row[1]), last_name=str(row[2]), userType=str(row[4]), department=str(row[5]))
                new_revo.set_password('TUPC-'+str(row[0])) #Default Password
                new_revo.save()
                messages.success(request, 'Successfully uploaded the staff account.')
                send_mail('TUP-Assist Account', 
                "Hello " + str(row[1]) + ',\n'
                '\nAs a staff of Technological University of the Philippines - Cavite, you are automatically registered in TUP-Assist.' + '\n\n'
                '\nTUP-Assist is a web-based system that helps Assist. Director of Academic Affairs, Department Head, Program-in-charge, and Teachers in adding, dropping, and transferring of subjects of students in TUP-Cavite.' + '\n\n'
                '\nAttached to this are your username/email and the default password that you can change later after logging in.' + '\n\n'
                'Username/Email: ' + str(row[3]) + '\n'
                'Password: ' + 'TUPC-'+str(row[0]) + '\n'
                'System Link: ' + 'https://tupassist.pythonanywhere.com' + '\n\n'
                'If there are any concerns, please reply to this email.' + '\n\n'
                'Thank you.', settings.EMAIL_HOST_USER , [str(row[3])], fail_silently=False)
            except:
                messages.error(request, 'Content of the csv does not not match to the format, or accounts are already exist create another file for the additional account.')
                return redirect('/a_account')
        return redirect('/a_account')
    return redirect('/a_account')

def a_staff_create(request):
    form = HeadRegistration()
    if request.method == 'POST':
        form = HeadRegistration(request.POST)
        if form.is_valid():
            form.save()
            first_name1 = form.cleaned_data.get('first_name')
            username1 = form.cleaned_data.get('username')
            email1 = form.cleaned_data.get('email')
            password1 = form.cleaned_data.get('password')
            userType1 = form.cleaned_data.get('userType')
            studID1 = form.cleaned_data.get('studID')
            send_mail('TUP-Assist Account', 
                "Hello " + str(first_name1) + ',\n'
                'As a ' + str(userType1) + ' of Technological University of the Philippines - Cavite, you are automatically registered in TUP-Assist.' + '\n\n'
                'TUP-Assist is a web-based system that helps students in adding, dropping, and transferring of subjects in TUP-Cavite.' + '\n\n'
                'Attached to this are your username/email and the default password that you can change later after logging in.' + '\n\n'
                'Username/Email: ' + str(username1) + '\n'
                "Password: " + str(studID1) +  '\n'
                'System Link: ' + 'https://tupassist.pythonanywhere.com' + '\n\n'
                'If there are any concerns, please reply to this email.' + '\n\n'
                'Thank you.', settings.EMAIL_HOST_USER , [email1], fail_silently=False)
            messages.success(request, 'Account successfully created!')
            return redirect ('/a_account')
        else:
            messages.error(request, 'Invalid Credentials!')
            return redirect ('/a_account')
    return render(request, 'TupAssistApp/a_account.html')

@login_required(login_url='/index')
def a_adding(request):
    if request.user.is_authenticated and (request.user.userType == 'OAA Staff' or request.user.is_superuser == True ):
        current_user = request.user = request.user
        req = AddingReq.objects.filter(admin_approve='Approved').order_by('-admin_date')
        cnt1 = len(AddingReq.objects.filter(reg_action='Pending'))
        cnt2 = len(AddingReq.objects.filter(reg_action='Approved'))
        context = { 
            'cnt1': cnt1,
            'cnt2': cnt2,
            'req': req,
            'current_user': current_user,
            }
        return render(request, 'TupAssistApp/a_adding.html', context)
    return redirect('/index')  

def a_approved_sub(request, id):
    edit = AddingReq.objects.get(id=id) 
    edit.reg_action = 'Approved'
    edit.enroll_by = request.user.first_name + ' ' + request.user.last_name
    edit.reg_date = datetime.now()
    edit.save()
    messages.success(request, 'Sucessfully enrolled the request!')
    # Email
    link = 'https://tupassist.pythonanywhere.com'
    data = registration.objects.get(studID=edit.studID_id) 
    send_mail('ADDING OF SUBJECT - REQUEST', 
    "Hi " + str(data.first_name) + ',' +
    '\n\nYour Request for Adding the ' + str(edit.subject.description) + ' in ' + str(edit.section) +
    " was already enrolled by the Registrar." + '\n\nYou may also check your request status by signing in your account on the attached link of our website.\n' + link
    , settings.EMAIL_HOST_USER , [data.email], fail_silently=False)
    return redirect('/a_adding/')

@login_required(login_url='/index')
def a_dropping(request):
    if request.user.is_authenticated and (request.user.userType == 'OAA Staff' or request.user.is_superuser == True ):
        current_user = request.user
        req = DroppingReq.objects.filter(admin_approve='Approve')
        context = {
            'req': req,
            'current_user': current_user
            }
        return render(request, 'TupAssistApp/a_dropping.html', context)
    return redirect('/index')  

@login_required(login_url='/index')
def a_transferring(request):
    if request.user.is_authenticated and (request.user.userType == 'OAA Staff' or request.user.is_superuser == True ):
        current_user = request.user
        req = TransferringReq.objects.filter(admin_approve='Approve')
        context = { 
            'req': req,
            'current_user': current_user
            }
        return render(request, 'TupAssistApp/a_transferring.html', context)
    return redirect('/index')  





# ADAA PAGES
@login_required(login_url='/index')
def adaa_profile(request):
    if request.user.is_authenticated and request.user.userType == 'Assist. Director of Academic Affairs':  
        current_user = request.user
        form = PasswordChangeForm(current_user)
        cnt1 = len(AddingReq.objects.filter(admin_approve='Pending'))
        context = {
            'cnt1': cnt1,
            'current_user': current_user,
            'form': form
        }
        return render(request, 'TupAssistApp/adaa_profile.html', context)
    return redirect('/index')

@login_required(login_url='/index')
def adaa_adding(request):
    if request.user.is_authenticated and request.user.userType == 'Assist. Director of Academic Affairs':
        current_user = request.user = request.user
        test = registration.objects.filter(Q(userType='Student') & (~Q(addStatus='') | Q(addStatus=None)) )
        cnt1 = len(AddingReq.objects.filter(admin_approve='Pending'))
        cnt2 = len(AddingReq.objects.filter(admin_approve='Approved'))
        context = {
            'cnt1': cnt1,
            'cnt2': cnt2,
            'test': test,
            'current_user': current_user,
            }
        return render(request, 'TupAssistApp/adaa_adding.html', context)
    return redirect('/index')

@login_required(login_url='/index')
def adaa_adding_view(request, studID):
    if request.user.is_authenticated and request.user.userType == 'Assist. Director of Academic Affairs':
        current_user = request.user
        data = registration.objects.get(studID=studID)
        req = AddingReq.objects.filter(Q(studID=data.studID) & (Q(admin_approve='Pending') | (Q(admin_approve='Approved')) )).order_by(('-admin_date'))
        print(req)
        context = { 
            'req': req,
            'current_user': current_user,
            'student_info': data,
            }
        return render(request, 'TupAssistApp/adaa_adding_view.html', context)
    return redirect('/index')


def adaa_approved_sub(request, id):
    edit = AddingReq.objects.get(id=id) 
    edit.admin_approve = 'Approved'
    edit.admin_name = request.user.first_name + ' ' + request.user.last_name
    edit.admin_date = datetime.now()
    edit.reg_action = 'Pending'
    edit.save()
    messages.success(request, 'Sucessfully approved the request!')
    # Email
    # link = 'https://tupassist.pythonanywhere.com'
    # data = registration.objects.get(studID=edit.studID_id) 
    # send_mail('ADDING OF SUBJECT - REQUEST', 
    # "Hi " + str(data.first_name) + ',' +
    # '\n\nYour Request for Adding the ' + str(edit.subject.description) + ' in ' + str(edit.section) +
    # " was already approved by ADAA. You need to wait for Registrar to enroll your subject. " + '\n\nYou may also check your request status by signing in your account on the attached link of our website.\n' + link
    # , settings.EMAIL_HOST_USER , [data.email], fail_silently=False)
    return redirect('/adaa_adding_view/'+ str(edit.studID_id))


def adaa_adding_approve(request):
    studID = request.POST.get('studID')
    admin_name = request.POST.get('admin_name')
    admin_date = datetime.now()
    data = registration.objects.get(studID=studID)
    if request.method =='POST':  
        AddingReq.objects.filter(Q(studID_id=studID) & (Q(head_is_approve='Approve')) & ((Q(admin_approve= None)) | (Q(admin_approve= ''))) ).update(admin_approve = 'Approve' , admin_name = admin_name , admin_date = admin_date)
        edit1 = registration.objects.get(studID=studID)
        edit1.addStatus = 'ADAA Approved'
        edit1.save()
        messages.success(request, 'Sucessfully edited the request!')
        # Email
        link = 'https://tupassist.pythonanywhere.com'
        content = 'Hi ' + data.first_name + ' ' + data.last_name + ',\n\nYour Request for Adding of Subject is already approved by ADAA. Check your request by signing in your account on the attached link. \n\n' + link
        send_mail('ADDING OF SUBJECT - REQUEST', 
            content, settings.EMAIL_HOST_USER , [data.email], fail_silently=False)
        return redirect('/adaa_adding_view/'+ str(data.studID))


@login_required(login_url='/index')
def adaa_dropping(request):
    if request.user.is_authenticated and request.user.userType == 'Assist. Director of Academic Affairs':
        current_user = request.user
        test = registration.objects.filter(Q(userType='Student') & (Q(dropStatus='Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval')) | Q(dropStatus='ADAA Approved')) 
        cnt1 = len(AddingReq.objects.filter(admin_approve='Pending'))
        context = {
            'cnt1': cnt1,
            'test': test,
            'current_user': current_user
            }
        return render(request, 'TupAssistApp/adaa_dropping.html', context)  
    return redirect('/index')

@login_required(login_url='/index')
def adaa_dropping_view(request, studID):
    if request.user.is_authenticated and request.user.userType == 'Assist. Director of Academic Affairs':
        current_user = request.user
        data = registration.objects.get(studID=studID)
        req = DroppingReq.objects.filter(studID=data.studID)
        context = { 
            'req': req,
            'current_user': current_user,
            'student_info': data,
            }
        return render(request, 'TupAssistApp/adaa_dropping_view.html', context)
    return redirect('/index')

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
        messages.success(request, 'Sucessfully edited the request!!')
        return redirect('/adaa_dropping_view/'+ str(data.studID))

@login_required(login_url='/index')
def adaa_dropping_approve(request):
    if request.user.is_authenticated and request.user.userType == 'Assist. Director of Academic Affairs':
        studID = request.POST.get('studID')
        admin_name = request.POST.get('admin_name')
        admin_date = datetime.now()
        data = registration.objects.get(studID=studID)
        if request.method =='POST':  
            DroppingReq.objects.filter(studID_id=studID).update(admin_approve = 'Approve')
            DroppingReq.objects.filter(studID_id=studID).update(admin_name = admin_name)
            DroppingReq.objects.filter(studID_id=studID).update(admin_date = admin_date)
            edit1 = registration.objects.get(studID=studID)
            edit1.dropStatus = 'ADAA Approved'
            edit1.save()
            messages.success(request, 'Sucessfully edited the request!')
            # Email
            link = 'tup-assist.com'
            content = 'Hi ' + data.first_name + ' ' + data.last_name + ',\n\n' + 'Your Request for Dropping of Subject is already approved by ADAA. Check your request by signing in your account on the attached link. \n\n' + link
            send_mail('DROPPING OF SUBJECT - REQUEST', 
                content, settings.EMAIL_HOST_USER , [data.email], fail_silently=False)
            return redirect('/adaa_dropping_view/'+ str(data.studID))
    return redirect('/index')     

@login_required(login_url='/index')
def adaa_transferring(request):
    if request.user.is_authenticated and request.user.userType == 'Assist. Director of Academic Affairs':
        current_user = request.user
        test = registration.objects.filter(Q(userType='Student') & (Q(transferStatus='Wait for Department Head and Assist. Director of Academic Affairs Approval')) | Q(transferStatus='ADAA Approved'))
        cnt1 = len(AddingReq.objects.filter(admin_approve='Pending'))
        context = { 
            'cnt1': cnt1,
            'test': test,
            'current_user': current_user
            }
        return render(request, 'TupAssistApp/adaa_transferring.html', context)
    return redirect('/index')

@login_required(login_url='/index')
def adaa_transferring_view(request, studID):
    if request.user.is_authenticated and request.user.userType == 'Assist. Director of Academic Affairs':
        current_user = request.user
        data = registration.objects.get(studID=studID)
        req = TransferringReq.objects.filter(studID=data.studID)
        context = { 
            'req': req,
            'current_user': current_user,
            'student_info': data,
            }
        return render(request, 'TupAssistApp/adaa_transferring_view.html', context)
    return redirect('/index')


def adaa_transferring_approve(request):
    studID = request.POST.get('studID')
    admin_name = request.POST.get('admin_name')
    admin_date = datetime.now()
    data = registration.objects.get(studID=studID)
    if request.method =='POST':  
        TransferringReq.objects.filter(studID_id=studID).update(admin_approve = 'Approve')
        TransferringReq.objects.filter(studID_id=studID).update(admin_name = admin_name)
        TransferringReq.objects.filter(studID_id=studID).update(admin_date = admin_date)
        edit1 = registration.objects.get(studID=studID)
        edit1.transferStatus = 'ADAA Approved'
        edit1.save()
        messages.success(request, 'Sucessfully edited the request!')
        # Email
        link = 'tup-assist.com'
        content = 'Hi ' + data.first_name + ' ' + data.last_name + ',\n\n' + 'Your Request for Transfer of Subject is already approved by ADAA. Check your request by signing in your account on the attached link. \n\n' + link
        send_mail('TRANSFERRING OF SUBJECT - REQUEST', 
            content, settings.EMAIL_HOST_USER , [data.email], fail_silently=False)
        return redirect('/adaa_transferring_view/'+ str(data.studID))



#STUDENT PAGES
@login_required(login_url='/index')
def s_profile(request):
    if request.user.is_authenticated and request.user.userType == 'Student':
        current_user = request.user
        form = PasswordChangeForm(current_user)
        # Models
        context = {
            'current_user': current_user,
            'form': form
        }
        return render(request, 'TupAssistApp/s_profile.html', context)
    return redirect('/index')

def changepassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Successfully changed the password!')
            return redirect('/s_profile')
        else:
            messages.error(request, 'Wrong password!')
            return redirect('/s_profile')

def changestudentinfo(request):
    current_user = request.user
    if request.method == 'POST':
        try:
            data = registration.objects.get(username=current_user.username)
            data.course = request.POST.get("course").upper()
            data.year = request.POST.get("year")
            data.section = request.POST.get("section").upper()
            data.studID = request.POST.get("studID")
            data.department = request.POST.get("department")
            data.save()
            messages.success(request, 'Successfully updated your personal information.')
            return redirect('/s_profile')
        except:
            messages.error(request, 'Invalid Credentials!')
            return redirect('/s_profile')
        
@login_required(login_url='/index')
def s_adding(request):
    if request.user.is_authenticated and request.user.userType == 'Student':
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
    return redirect('/index')



def upload(request):
    current_user = request.user
    if request.method == 'POST':
        data = registration.objects.get(username=current_user.username)
        data.upload = request.FILES["gradesfile"]
        data.save()
        messages.success(request, 'Successfully uploaded your file.')
        return redirect('/s_adding')

def upload1(request):
    current_user = request.user
    if request.method == 'POST':
        data = registration.objects.get(username=current_user.username)
        data.plot_sheet_link = request.FILES["plot_sheet_link"]
        data.save()
        messages.success(request, 'Successfully uploaded your file.')
        return redirect('/s_adding')

def delupload(request):
    current_user = request.user
    data = registration.objects.get(username=current_user.username)
    data.upload = ""
    data.save()
    return redirect('/s_adding')

def delupload1(request):
    current_user = request.user
    data = registration.objects.get(username=current_user.username)
    data.plot_sheet_link = ""
    data.save()
    return redirect('/s_adding')

def s_add_sub(request):
    current_user = request.user
    if request.method =='POST':
        school_year = request.POST.get('school_year')
        semester = request.POST.get('semester')
        subject = request.POST.get('subject')
        section = request.POST.get('section').upper()
        schedule = request.POST.get('schedule')
        datetime1 = datetime.now()
        slots = len(AddingReq.objects.filter(Q(school_year=school_year) & Q(semester=semester) & Q(subject=subject) & Q(section=section) & Q(pic_is_approve='Approve')))
        print(slots)
        if slots == 10:
            messages.error(request, "Sorry, there is no slots available for this subject and section already.")
            return redirect('/s_adding')
        else:
            exist = len(AddingReq.objects.filter(Q(studID_id=current_user.studID) & Q(school_year=school_year) & Q(semester=semester) & Q(subject=subject)))
            print(exist)
            if exist == 0:
                data = AddingReq.objects.create(school_year=school_year, semester=semester, studID_id= current_user.studID, subject_id=subject, section=section, sched=schedule, req_date=datetime1, pic_is_approve='Pending')
                data.save()
                messages.success(request, 'Subject Added')
                return redirect('/s_adding')
            else:
                messages.error(request, 'Subject already existed.')
                return redirect('/s_adding')

def s_del_sub(request, id):
    data = AddingReq.objects.get(id=id)
    data.delete()
    messages.success(request, 'Subject deleted')
    return redirect('/s_adding')

def s_step1_submit(request):
    current_user = request.user
    if request.method =='POST':
        grade = request.POST.get("grade")
        plot = request.POST.get("plot")
        not_empty = request.POST.get("not_empty")
        if (not_empty == '' or not_empty == None):
            messages.error(request, 'Add subject first.')
            return redirect('/s_adding')
        elif (grade == '' or grade == None):
            messages.error(request, 'Upload a compile of your grades first.')
            return redirect('/s_adding')
        elif  (plot == '' or plot == None):
            messages.error(request, 'Upload Image/Screenshot of your Plotted Schedule from your customized google sheet/excel file.')
            return redirect('/s_adding')
        else:
            data = registration.objects.get(username=current_user.username)
            data.addStatus = "Wait for PIC, Department head, ADAA and Registrar's Action"
            data.addDate = datetime.now()
            data.save()
            messages.success(request, 'Request submitted')
            return redirect('/s_adding')
           
def s_edit_sub(request):
    if request.method =='POST':
        id = request.POST.get('id')
        data = AddingReq.objects.get(id=id)
        data.subject_id = request.POST.get('subject')
        data.section = request.POST.get('section').upper()
        data.req_date = datetime.now()

        # Time Handling error
        a = request.POST.get('mon_start1')
        b = request.POST.get('mon_end1')
        c = request.POST.get('tue_start1')
        d = request.POST.get('tue_end1')
        e = request.POST.get('wed_start1')
        f = request.POST.get('wed_end1')
        g = request.POST.get('thu_start1')
        h = request.POST.get('thu_end1')
        i = request.POST.get('fri_start1')
        j = request.POST.get('fri_end1')
        k = request.POST.get('sat_start1')
        l = request.POST.get('sat_end1')

        arr = []


        if (a == '' and b == '' and c == '' and d == '' and e == '' and f == '' and g == '' and h == '' and i == '' and j == '' and k == '' and l == '')  :
            data.sched = None
            data.save()
            messages.success(request, 'Successfuly updated the request.')
            return redirect('/s_adding')

        elif (b <= a and (a and b != '')) or (d <= c and (c and d != '')) or (f <= e and (e and f != '')) or (h <= g and (h and g != '')) or (j <= i and (i and j != '')) or (l <= k  and (k and l != '')):
            data.save()
            messages.error(request, 'Wrong input of time start and end time!')
            return redirect('/s_adding')

        else :
            if b > a and (a and b != '') :
                # Conversion of 24 form to 12hr format
                a1 = datetime.strptime(a, "%H:%M")
                b1 = datetime.strptime(b, "%H:%M")
                arr.append('M'  + ' ' + a1.strftime("%I:%M %p") + '-' + b1.strftime("%I:%M %p"))
            if d > c and (c and d != '') :
                # Conversion of 24 form to 12hr format
                c1 = datetime.strptime(c, "%H:%M")
                d1 = datetime.strptime(d, "%H:%M")
                arr.append('T'  + ' ' + c1.strftime("%I:%M %p")  + '-' + d1.strftime("%I:%M %p")) 
            if f > e and (e and f != '') :
                # Conversion of 24 form to 12hr format
                e1 = datetime.strptime(e, "%H:%M")
                f1 = datetime.strptime(f, "%H:%M")
                arr.append('W'  + ' ' + e1.strftime("%I:%M %p")  + '-' + f1.strftime("%I:%M %p"))
            if h > g and (h and g != '') :
                # Conversion of 24 form to 12hr format
                g1 = datetime.strptime(g, "%H:%M")
                h1 = datetime.strptime(h, "%H:%M")
                arr.append('TH'  + ' ' + g1.strftime("%I:%M %p")  + '-' + h1.strftime("%I:%M %p"))    
            if j > i and (i and j != '') :
                # Conversion of 24 form to 12hr format
                i1 = datetime.strptime(i, "%H:%M")
                j1 = datetime.strptime(j, "%H:%M")
                arr.append('F'  + ' ' + i1.strftime("%I:%M %p")  + '-' + j1.strftime("%I:%M %p")) 
            if l > k and (k and l != '') :
                # Conversion of 24 form to 12hr format
                k1 = datetime.strptime(k, "%H:%M")
                l1 = datetime.strptime(l, "%H:%M")
                arr.append('S'  + ' ' + k1.strftime("%I:%M %p")  + '-' + l1.strftime("%I:%M %p"))    
        
            
            # data.sched = str(arr)[2:-2]
            data.sched = ("[{0}]".format( ', '.join(map(str, arr))))[1:-1]
            data.save() 
            messages.success(request, 'Successfuly updated the request.')
            return redirect('/s_adding')
       
def s_step2_submit(request):
    # current_user = request.user
    # data = registration.objects.get(username=current_user.username)
    # data.addStatus = 'Updated Request'
    # data.save()
    return redirect('/s_adding')


@login_required(login_url='/index')
def s_dropping(request):
    if request.user.is_authenticated and request.user.userType == 'Student':
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
    return redirect('/index')

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
            subject = 'DROPPING SUBJECT REQUEST'
            link = 'https://tupassist.pythonanywhere.com'
            content = 'Good day!, \n\n' + current_user.first_name + ' ' + current_user.last_name + ' is requesting to drop on your subject,' + subject1 + ' Due to this reason: '+ reason + '\n\n Please click this link below to login. Use your gsfe eamil and the deault password is your id number. Ex. TUPC-190123 \n\n' + link
            send_mail(subject, 
                content, settings.EMAIL_HOST_USER , [teacher1], fail_silently=False)
        if subject2 and section2 and schedule2 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject2, section=section2, sched=schedule2, subj_teacher_name=teacher2, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
            subject = 'DROPPING SUBJECT REQUEST'
            link = 'https://tupassist.pythonanywhere.com'
            content = 'Good day!, \n\n' + current_user.first_name + ' ' + current_user.last_name + ' is requesting to drop on your subject,' + subject2 + ' Due to this reason: '+ reason + '\n\n Please click this link below to login. Use your gsfe eamil and the deault password is your id number. Ex. TUPC-190123 \n\n' + link
            send_mail(subject, 
                content, settings.EMAIL_HOST_USER , [teacher2], fail_silently=False)
        
                
        if subject3 and section3 and schedule3 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject3, section=section3, sched=schedule3, subj_teacher_name=teacher3, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
            subject = 'DROPPING SUBJECT REQUEST'
            link = 'https://tupassist.pythonanywhere.com'
            content = 'Good day!, \n\n' + current_user.first_name + ' ' + current_user.last_name + ' is requesting to drop on your subject,' + subject3 + ' Due to this reason:'+ reason + '\n\n Please click this link below to login. Use your gsfe eamil and the deault password is your id number. Ex. TUPC-190123 \n\n' + link
            send_mail(subject, 
                content, settings.EMAIL_HOST_USER , [teacher3], fail_silently=False)
            
        if subject4 and section4 and schedule4 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject4, section=section4, sched=schedule4, subj_teacher_name=teacher4, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
            subject = 'DROPPING SUBJECT REQUEST'
            link = 'https://tupassist.pythonanywhere.com'
            content = 'Good day!, \n\n' + current_user.first_name + ' ' + current_user.last_name + ' is requesting to drop on your subject,' + subject4 + ' Due to this reason:'+ reason + '\n\n Please click this link below to login. Use your gsfe eamil and the deault password is your id number. Ex. TUPC-190123 \n\n' + link
            send_mail(subject, 
                content, settings.EMAIL_HOST_USER , [teacher4], fail_silently=False)
            
        if subject5 and section5 and schedule5 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject5, section=section5, sched=schedule5, subj_teacher_name=teacher5, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
            subject = 'DROPPING SUBJECT REQUEST'
            link = 'https://tupassist.pythonanywhere.com'
            content = 'Good day!, \n\n' + current_user.first_name + ' ' + current_user.last_name + ' is requesting to drop on your subject,' + subject5 + ' Due to this reason:'+ reason + '\n\n Please click this link below to login. Use your gsfe eamil and the deault password is your id number. Ex. TUPC-190123 \n\n' + link
            send_mail(subject, 
                content, settings.EMAIL_HOST_USER , [teacher5], fail_silently=False)
            
        if subject6 and section6 and schedule6 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject6, section=section6, sched=schedule6, subj_teacher_name=teacher6, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
            subject = 'DROPPING SUBJECT REQUEST'
            link = 'https://tupassist.pythonanywhere.com'
            content = 'Good day!, \n\n' + current_user.first_name + ' ' + current_user.last_name + ' is requesting to drop on your subject,' + subject6 + ' Due to this reason:'+ reason + '\n\n Please click this link below to login. Use your gsfe eamil and the deault password is your id number. Ex. TUPC-190123 \n\n' + link
            send_mail(subject, 
                content, settings.EMAIL_HOST_USER , [teacher6], fail_silently=False)


        if subject7 and section7 and schedule7 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject7, section=section7, sched=schedule7, subj_teacher_name=teacher7, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
            subject = 'DROPPING SUBJECT REQUEST'
            link = 'https://tupassist.pythonanywhere.com'
            content = 'Good day!, \n\n' + current_user.first_name + ' ' + current_user.last_name + ' is requesting to drop on your subject,' + subject7 + ' Due to this reason:'+ reason + '\n\n Please click this link below to login. Use your gsfe eamil and the deault password is your id number. Ex. TUPC-190123 \n\n' + link
            send_mail(subject, 
                content, settings.EMAIL_HOST_USER , [teacher7], fail_silently=False)


        if subject8 and section8 and schedule8 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject8, section=section8, sched=schedule8, subj_teacher_name=teacher8, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
            subject = 'DROPPING SUBJECT REQUEST'
            link = 'https://tupassist.pythonanywhere.com'
            content = 'Good day!, \n\n' + current_user.first_name + ' ' + current_user.last_name + ' is requesting to drop on your subject,' + subject8 + ' Due to this reason:'+ reason + '\n\n Please click this link below to login. Use your gsfe eamil and the deault password is your id number. Ex. TUPC-190123 \n\n' + link
            send_mail(subject, 
                content, settings.EMAIL_HOST_USER , [teacher8], fail_silently=False)


        if subject9 and section9 and schedule9 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject9, section=section9, sched=schedule9, subj_teacher_name=teacher9, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
            subject = 'DROPPING SUBJECT REQUEST'
            link = 'https://tupassist.pythonanywhere.com'
            content = 'Good day!, \n\n' + current_user.first_name + ' ' + current_user.last_name + ' is requesting to drop on your subject,' + subject9 + ' Due to this reason: '+ reason + '\n\n Please click this link below to login. Use your gsfe eamil and the deault password is your id number. Ex. TUPC-190123 \n\n' + link
            send_mail(subject, 
                content, settings.EMAIL_HOST_USER , [teacher9], fail_silently=False)

        if subject10 and section10 and schedule10 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject10, section=section10, sched=schedule10, subj_teacher_name=teacher10, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
            subject = 'DROPPING SUBJECT REQUEST'
            link = 'https://tupassist.pythonanywhere.com'
            content = 'Good day!, \n\n' + current_user.first_name + ' ' + current_user.last_name + ' is requesting to drop on your subject,' + subject10 + ' Due to this reason: '+ reason + '\n\n Please click this link below to login. Use your gsfe eamil and the deault password is your id number. Ex. TUPC-190123 \n\n' + link
            send_mail(subject, 
                content, settings.EMAIL_HOST_USER , [teacher10], fail_silently=False)


        if subject11 and section11 and schedule11 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject11, section=section11, sched=schedule11, subj_teacher_name=teacher11, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
            subject = 'DROPPING SUBJECT REQUEST'
            link = 'https://tupassist.pythonanywhere.com'
            content = 'Good day!, \n\n' + current_user.first_name + ' ' + current_user.last_name + ' is requesting to drop on your subject,' + subject11 + ' Due to this reason: '+ reason + '\n\n Please click this link below to login. Use your gsfe eamil and the deault password is your id number. Ex. TUPC-190123 \n\n' + link
            send_mail(subject, 
                content, settings.EMAIL_HOST_USER , [teacher11], fail_silently=False)


        if subject12 and section12 and schedule12 !='':
            data = DroppingReq.objects.create(studID_id= current_user.studID, subject_id=subject12, section=section12, sched=schedule12, subj_teacher_name=teacher12, reason=reason)
            data.save()
            data1 = registration.objects.get(studID=current_user.studID)
            data1.dropStatus = 'Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval'
            data1.save()
            subject = 'DROPPING SUBJECT REQUEST'
            link = 'https://tupassist.pythonanywhere.com'
            content = 'Good day!, \n\n' + current_user.first_name + ' ' + current_user.last_name + ' is requesting to drop on your subject,' + subject12 + ' Due to this reason: '+ reason + '\n\n Please click this link below to login. Use your gsfe eamil and the deault password is your id number. Ex. TUPC-190123 \n\n' + link
            send_mail(subject, 
                content, settings.EMAIL_HOST_USER , [teacher12], fail_silently=False)

        messages.success(request, 'Subject to Drop Successfully Request Wait for the Teacher Approval.')
        return redirect('/s_dropping')


@login_required(login_url='/index')
def s_transferring(request):
    if request.user.is_authenticated and request.user.userType == 'Student':
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
    return redirect('/index')


def s_trans_sub(request):
    current_user = request.user
    if request.method =='POST':
        school_year = request.POST.get('school_year')
        semester = request.POST.get('semester')
        subject = request.POST.get('subject')
        section = request.POST.get('section').upper()
        schedule = request.POST.get('schedule')
        reason = request.POST.get('reason')
        data = TransferringReq.objects.create(school_year=school_year, semester=semester, studID_id= current_user.studID, subject_id=subject, section=section, sched=schedule, reason=reason)
        data.save()
        messages.success(request, 'Subject tranfer request added.')
        return redirect('/s_transferring')

def s_del_sub_t(request, id):
    data = TransferringReq.objects.get(id=id)
    data.delete()
    messages.success(request, 'Subject Deleted')
    return redirect('/s_transferring')

def s_step1_submit_t(request):
    current_user = request.user
    if request.method =='POST':
        not_empty = request.POST.get("not_empty")
        if (not_empty == '' or not_empty == None):
            messages.error(request, 'Transfer Subject First.')
            return redirect('/s_transferring')    
        else: 
            data = registration.objects.get(username=current_user.username)
            data.transferStatus = 'Wait for Department Head and Asst. Director for Academic Affairs Approval'
            data.save()
            messages.success(request, 'Request submitted')
            return redirect('/s_transferring')





# PIC PAGES
@login_required(login_url='/index')
def p_profile(request):
    if request.user.is_authenticated and request.user.userType == 'Program-in-charge':
        current_user = request.user
        cnt = len(AddingReq.objects.filter(pic_is_approve='Pending'))
        form = PasswordChangeForm(current_user)
        context = {
            'cnt': cnt,
            'current_user': current_user,
            'form': form
        }
        return render(request, 'TupAssistApp/p_profile.html', context)
    return redirect('/index')

def changepassword1(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Successfully changed the password.')
            return redirect('/p_profile')
        else:
            messages.error(request, 'Wrong password!')
            return redirect('/p_profile')

def changepicinfo(request):
    current_user = request.user
    if request.method == 'POST':
        try:
            data = registration.objects.get(username=current_user.username)
            data.course = request.POST.get("course").upper()
            data.studID = request.POST.get("studID")
            data.department = request.POST.get("department")
            data.save()
            messages.success(request, 'Successfully updated your Personal Information.')
            return redirect('/p_profile')
        except:
            messages.error(request, 'Invalid Credentials!')
            return redirect('/p_profile')

@login_required(login_url='/index')
def p_adding(request):
    if request.user.is_authenticated and request.user.userType == 'Program-in-charge':
        current_user = request.user
        test = registration.objects.filter(Q(course=current_user.course) & Q(userType='Student') & ~Q(addStatus='')).order_by('addDate')
        cnt1 = len(AddingReq.objects.filter(Q(studID__course=current_user.course) & Q(pic_is_approve='Declined')))
        cnt2 = len(AddingReq.objects.filter(Q(studID__course=current_user.course) & Q(pic_is_approve='Pending')))
        cnt3 = len(AddingReq.objects.filter(Q(studID__course=current_user.course) & Q(pic_is_approve='Approved')))
        context = { 
            'cnt1': cnt1,
            'cnt2': cnt2,
            'cnt3': cnt3,
            'test': test,
            'current_user': current_user
            }
        return render(request, 'TupAssistApp/p_adding.html', context )
    return redirect('/index')

@login_required(login_url='/index')
def p_adding_edit(request, studID):
    if request.user.is_authenticated and request.user.userType == 'Program-in-charge':
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
                'trans': trans
    
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
                'trans': trans
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
                'trans': trans
            }
        else:
            context = {
                'current_user': current_user,
                'student_info': student_info,
                'req': req,
                'sched': sched,
                'trans': trans
            }
        return render(request, 'TupAssistApp/p_adding_edit.html', context)
    return redirect('/index')

def p_edit_sub(request):
    studID = request.POST.get('studID')
    data = registration.objects.get(studID=studID)
    if request.method =='POST':
        id = request.POST.get('id')
        school_year = request.POST.get('school_year')
        semester = request.POST.get('semester')
        subject = request.POST.get('subject')
        section = request.POST.get('section').upper()
        slots = len(AddingReq.objects.filter(Q(school_year=school_year) & Q(semester=semester) & Q(subject=subject) & Q(section=section) & Q(pic_is_approve='Approve')))
        print(slots)
        if slots == 10:
            messages.error(request, "Sorry, there is no slots available for this subject and section already.")
            return redirect('/p_adding_edit/'+ str(data.studID))
        else:
            exist = len(AddingReq.objects.filter(Q(studID_id=studID) & Q(school_year=school_year) & Q(semester=semester) & Q(subject=subject)))
            print(exist)
            if exist == 0:
                subject = request.POST.get('subject')
                section = request.POST.get('section').upper()
                sched = request.POST.get('sched')
                pic_is_approve = request.POST.get('pic_is_approve')
                pic_remark = request.POST.get('pic_remark')
                pic_name = request.POST.get('pic_name')
                edit = AddingReq.objects.get(id=id)
                edit.section = request.POST.get('section').upper()
                edit.sched = request.POST.get('sched')
                edit.pic_is_approve = request.POST.get('pic_is_approve')
                edit.pic_remark = request.POST.get('pic_remark')
                edit.pic_name = request.POST.get('pic_name')
                edit.pic_date = datetime.now()
                if request.POST.get('pic_is_approve') == 'Approved':
                    edit.head_is_approve = 'Pending'
                    edit.save()
                    messages.success(request, 'Request successfully edited!')
                    content = 'Good day! \n\n' + str(pic_name) + " " + str(pic_is_approve) + ' your request for ' + str(subject) + ' ' + str(section) + '\n\nRemarks: ' + str(pic_remark)
                    send_mail('ADDING OF SUBJECT - REQUEST', 
                    content, settings.EMAIL_HOST_USER , [data.email], fail_silently=False)
                    return redirect('/p_adding_edit/'+ str(data.studID))
                else:
                    edit.save()
                    messages.success(request, 'Request successfully edited!')
                    content = 'Good day! \n\n' + str(pic_name) + " " + str(pic_is_approve) + ' your request for ' + str(subject) + ' ' + str(section) + '\n\nRemarks: ' + str(pic_remark)
                    send_mail('ADDING OF SUBJECT - REQUEST', 
                    content, settings.EMAIL_HOST_USER , [data.email], fail_silently=False)
                    return redirect('/p_adding_edit/'+ str(data.studID))
            else:
                messages.error(request, 'Subject already existed.')
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
        # Condition for slots availability
        slots = len(AddingReq.objects.filter(Q(school_year=school_year) & Q(semester=semester) & Q(subject=subject) & Q(section=section) & Q(pic_is_approve='Approve')))
        print(slots)
        if slots == 10:
            messages.error(request, "Sorry, there is no slots available for this subject and section already.")
            return redirect('/p_adding_edit/'+ str(data.studID))
        else:
            # exist = len(AddingReq.objects.filter(Q(studID_id=studID) & Q(school_year=school_year) & Q(semester=semester) & Q(subject=subject)))
            # print(exist)
            add = AddingReq.objects.create(school_year=school_year, semester=semester, studID_id=studID, subject_id=subject, section=section, sched=sched, pic_is_approve=pic_is_approve, pic_remark=pic_remark, pic_name=pic_name, pic_date=pic_date)
            add.save()
            messages.success(request, 'Subject successfully added!')
            return redirect('/p_adding_edit/'+ str(data.studID))

def p_step1_submit(request):
    studID = request.POST.get('studID')
    if request.method =='POST':
        data = registration.objects.get(studID=studID)
        data.addStatus = 'Wait for Department Head and Asst. Director for Academic Affairs Approval'
        data.save()
        return redirect('/p_adding_edit/'+ str(data.studID))


@login_required(login_url='/index')
def p_requests(request):
    if request.user.is_authenticated and request.user.userType == 'Program-in-charge':
        current_user = request.user
        cnt = len(AddingReq.objects.filter(pic_is_approve='Pending'))
        req = DroppingReq.objects.filter(subj_teacher_name=current_user.email)
        context = {
            'cnt': cnt,
            'current_user': current_user,
            'req': req,
        }
        return render(request, 'TupAssistApp/p_requests.html', context)
    return redirect('/index')  

def p_edit_sub1(request):
    if request.method =='POST':
        id = request.POST.get('id')   
        edit = DroppingReq.objects.get(id=id)
        edit.section = request.POST.get('section').upper()
        edit.sched = request.POST.get('sched')
        edit.subj_teacher_approve = request.POST.get('subj_teacher_approve')
        edit.subj_teacher_remark = request.POST.get('subj_teacher_remark')
        edit.subj_teacher_name = request.POST.get('subj_teacher_name')
        edit.subj_teacher_date = datetime.now()
        edit.save()
        messages.success(request, 'Successfully edited the request!')
        return redirect('/p_requests')
        

#  TEACHER PAGES
@login_required(login_url='/index')
def t_profile(request):
    if request.user.is_authenticated and request.user.userType == 'Teacher':
        current_user = request.user
        form = PasswordChangeForm(current_user)
        context = {
            'current_user': current_user,
            'form': form
        }
        return render(request, 'TupAssistApp/t_profile.html', context)
    return redirect('/index')

@login_required(login_url='/index')
def t_requests(request):
    if request.user.is_authenticated and request.user.userType == 'Teacher':
        current_user = request.user
        req = DroppingReq.objects.filter(subj_teacher_name=current_user.email)
        context = {
            'current_user': current_user,
            'req': req,
        }
        return render(request, 'TupAssistApp/t_requests.html', context)
    return redirect('/index')

def t_edit_sub(request):
    if request.method =='POST':
        id = request.POST.get('id')   
        edit = DroppingReq.objects.get(id=id)
        edit.section = request.POST.get('section').upper()
        edit.sched = request.POST.get('sched')
        edit.subj_teacher_approve = request.POST.get('subj_teacher_approve')
        edit.subj_teacher_remark = request.POST.get('subj_teacher_remark')
        edit.subj_teacher_name = request.POST.get('subj_teacher_name')
        edit.subj_teacher_date = datetime.now()
        edit.save()
        messages.success(request, 'Successfully edited the request')
        return redirect('/t_requests')





# DEPARTMENT HEAD PAGES
@login_required(login_url='/index')
def h_profile(request):
    if request.user.is_authenticated and request.user.userType == 'Department Head':
        current_user = request.user
        form = PasswordChangeForm(current_user)
        cnt2 = len(AddingReq.objects.filter(Q(studID__department=current_user.department) & Q(head_is_approve='Pending')))
        context = {
            'cnt2': cnt2,
            'current_user': current_user,
            'form': form
        }
        return render(request, 'TupAssistApp/h_profile.html', context)
    return redirect('/index')

def changepassword2(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Successfully changed the password.')
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
            messages.success(request, 'Successfully updated your Personal Information.')
            return redirect('/h_profile')
        except:
            messages.error(request, 'Invalid Credentials!')
            return redirect('/h_profile')

@login_required(login_url='/index')
def h_subject(request):
    if request.user.is_authenticated and request.user.userType == 'Department Head':
        current_user = request.user
        if current_user.department == "Department of Industrial Technology":
            current_user.department1 = "DIT"
            current_user.department2 = "BET"
            subs = Subjects.objects.filter (Q(course__icontains=current_user.department1) | Q(course__icontains=current_user.department2) ) 
            cnt2 = len(AddingReq.objects.filter(Q(studID__department=current_user.department) & Q(head_is_approve='Pending')))
            context = {
                'cnt2': cnt2,
                'current_user': current_user,
                'subs': subs,
                }
        elif current_user.department == "Department of Engineering":
            current_user.department1 = "DOE"
            current_user.department2 = "BSCE"
            subs = Subjects.objects.filter (Q(course__icontains=current_user.department1) | Q(course__icontains=current_user.department2) ) 
            cnt2 = len(AddingReq.objects.filter(Q(studID__department=current_user.department) & Q(head_is_approve='Pending')))
            context = {
                'cnt2': cnt2,
                'current_user': current_user,
                'subs': subs,
            }
        elif current_user.department == "Department of Industrial Education":
            current_user.department1 = "DIE"
            current_user.department2 = "BSIE-ICT"
            subs = Subjects.objects.filter (Q(course__icontains=current_user.department1) | Q(course__icontains=current_user.department2) ) 
            cnt2 = len(AddingReq.objects.filter(Q(studID__department=current_user.department) & Q(head_is_approve='Pending')))
            context = {
                'cnt2': cnt2,
                'current_user': current_user,
                'subs': subs,
            }
        elif current_user.department == "Department of Math and Science":
            current_user.department1 = "DMS"
            subs = Subjects.objects.filter (Q(course__icontains=current_user.department1)) 
            cnt2 = len(AddingReq.objects.filter(Q(studID__department=current_user.department) & Q(head_is_approve='Pending')))
            context = {
                'cnt2': cnt2,
                'current_user': current_user,
                'subs': subs,
            }
        elif current_user.department == "Department of Liberal Arts":
            current_user.department1 = "DLA"
            subs = Subjects.objects.filter (Q(course__icontains=current_user.department1)) 
            cnt2 = len(AddingReq.objects.filter(Q(studID__department=current_user.department) & Q(head_is_approve='Pending')))
            context = {
                'cnt2': cnt2,
                'current_user': current_user,
                'subs': subs,
            }
        return render(request, 'TupAssistApp/h_subject.html', context)
    return redirect('/index') 

def sub_cvs(request):
    current_user = request.user
    if request.method=='POST': 
        if current_user.department == 'Department of Industrial Technology':
            subcvsfile = request.FILES["subcvsfile"]
            decoded_file = subcvsfile.read().decode('utf-8').splitlines()[1:]
            reader = csv.reader(decoded_file)
            for row in reader:
                try:
                    new_revo = Subjects.objects.create(subject=str(row[0])+str(row[1])+str(row[2])+str(row[3]), course=str(row[0]), year=int(row[1]), semester=int(row[2]), shop=int(row[3]), description=str(row[4]))
                    new_revo.save()
                    messages.success(request, 'Successfully updated the subjects')
                except:
                    messages.error(request, 'Content of the csv does not match to the format, or subjects are already existed create another file for the additional subject.')
                    return redirect('/h_subject')
            return redirect('/h_subject')
        elif current_user.department == 'Department of Industrial Education':
            subcvsfile = request.FILES["subcvsfile"]
            decoded_file = subcvsfile.read().decode('utf-8').splitlines()[1:]
            reader = csv.reader(decoded_file)
            for row in reader:
                try:
                    new_revo = Subjects.objects.create(subject=str(row[0])+str(row[1])+str(row[2])+str(row[3]), course=str(row[0]), year=int(row[1]), semester=int(row[2]), shop=int(row[3]), description=str(row[4]))
                    new_revo.save()
                    messages.success(request, 'Successfully updated the subjects')
                except:
                    messages.error(request, 'Content of the csv does not match to the format, or subjects are already existed create another file for the additional subject.')
                    return redirect('/h_subject')
            return redirect('/h_subject')
        elif current_user.department == 'Department of Engineering':
            subcvsfile = request.FILES["subcvsfile"]
            decoded_file = subcvsfile.read().decode('utf-8').splitlines()[1:]
            reader = csv.reader(decoded_file)
            for row in reader:
                try:
                    new_revo = Subjects.objects.create(subject=str(row[0])+str(row[1])+str(row[2])+str(row[3]), course=str(row[0]), year=int(row[1]), semester=int(row[2]), shop=int(row[3]), description=str(row[4]))
                    new_revo.save()
                    messages.success(request, 'Successfully updated the subjects')
                except:
                    messages.error(request, 'Content of the csv does not match to the format, or subjects are already existed create another file for the additional subject.')
                    return redirect('/h_subject')
            return redirect('/h_subject')
        elif current_user.department == 'Department of Math and Science':
            subcvsfile = request.FILES["subcvsfile"]
            decoded_file = subcvsfile.read().decode('utf-8').splitlines()[1:]
            reader = csv.reader(decoded_file)
            for row in reader:
                try:
                    new_revo = Subjects.objects.create(subject=str(row[0])+str(row[1])+str(row[2])+str(row[3]), course=str(row[0]), year=int(row[1]), semester=int(row[2]), shop=int(row[3]), description=str(row[4]))
                    new_revo.save()
                    messages.success(request, 'Successfully updated the subjects')
                except:
                    messages.error(request, 'Content of the csv does not match to the format, or subjects are already existed create another file for the additional subject.')
                    return redirect('/h_subject')
            return redirect('/h_subject')
        elif current_user.department == 'Department of Liberal Arts':
            # junk = Subjects.objects.filter(course='DLA')
            # junk.delete()
            subcvsfile = request.FILES["subcvsfile"]
            decoded_file = subcvsfile.read().decode('utf-8').splitlines()[1:]
            reader = csv.reader(decoded_file)
            for row in reader:
                try:
                    new_revo = Subjects.objects.create(subject=str(row[0])+str(row[1])+str(row[2])+str(row[3]), course=str(row[0]), year=int(row[1]), semester=int(row[2]), shop=int(row[3]), description=str(row[4]))
                    new_revo.save()
                    messages.success(request, 'Successfully updated the subjects')
                except:
                    messages.error(request, 'Content of the csv does not match to the format, or subjects are already existed create another file for the additional subject.')
                    return redirect('/h_subject')
            return redirect('/h_subject')
    return redirect('/h_subject')


@login_required(login_url='/index')
def h_logs(request):
    if request.user.is_authenticated and request.user.userType == 'Department Head':
        current_user = request.user
        staff = registration.objects.filter(Q(userType='Program-in-Charge') & Q(department=request.user.department))
        context = {
            'current_user': current_user,
            'staff': staff
        }
        return render(request, 'TupAssistApp/h_logs.html', context)
    return redirect('/index')



@login_required(login_url='/index')
def h_adding(request):
    if request.user.is_authenticated and request.user.userType == 'Department Head':
        current_user = request.user
        if current_user.department == "Department of Industrial Technology" or current_user.department == "Department of Engineering" or current_user.department == "Department of Industrial Education":
            test = registration.objects.filter(Q(department=current_user.department) & Q(userType='Student') & (~Q(addStatus='')))
            cnt1 = len(AddingReq.objects.filter(Q(studID__department=current_user.department) & Q(head_is_approve='Declined')))
            cnt2 = len(AddingReq.objects.filter(Q(studID__department=current_user.department) & Q(head_is_approve='Pending')))
            cnt3 = len(AddingReq.objects.filter(Q(studID__department=current_user.department) & Q(head_is_approve='Approved')))
            context = { 
                'cnt1': cnt1,
                'cnt2': cnt2,
                'cnt3': cnt3,
                'test': test,
                'current_user': current_user
                }
        else:
            test = registration.objects.filter(Q(userType='Student') & (~Q(addStatus='')))
            cnt1 = len(AddingReq.objects.filter(Q(studID__department=current_user.department) & Q(head_is_approve='Declined')))
            cnt2 = len(AddingReq.objects.filter(Q(studID__department=current_user.department) & Q(head_is_approve='Pending')))
            cnt3 = len(AddingReq.objects.filter(Q(studID__department=current_user.department) & Q(head_is_approve='Approved')))
            context = { 
                'cnt1': cnt1,
                'cnt2': cnt2,
                'cnt3': cnt3,
                'test': test,
                'current_user': current_user
                }
        return render(request, 'TupAssistApp/h-adding.html', context)
    return redirect('/index') 

@login_required(login_url='/index')
def h_adding_edit(request, studID):
    if request.user.is_authenticated and request.user.userType == 'Department Head':
        current_user = request.user
        data = registration.objects.get(studID=studID)
        sched = Schedule.objects.all()
        if current_user.department == "Department of Industrial Technology":
            department1 = "DIT"
            course1 = "BET-COET"
            req = AddingReq.objects.filter(Q (studID_id=data.studID) & (Q(subject_id__course=department1) | (Q(subject_id__course=course1))))
            context = { 
                'current_user': current_user,
                'student_info': data,
                'req': req,
                'sched': sched
                }
        elif current_user.department == "Department of Industrial Education":
            department1 = "DIE"
            course1 = "BS-ICT"
            req = AddingReq.objects.filter(Q (studID_id=data.studID) & (Q(subject_id__course=department1) | (Q(subject_id__course=course1))))
            context = { 
                'current_user': current_user,
                'student_info': data,
                'req': req,
                'sched': sched
                }
        elif current_user.department == "Department of Engineering":
            department1 = "DOE"
            course1 = "BSCE"
            req = AddingReq.objects.filter(Q (studID_id=data.studID) & (Q(subject_id__course=department1) | (Q(subject_id__course=course1))))
            context = { 
                'current_user': current_user,
                'student_info': data,
                'req': req,
                'sched': sched
                }
        elif current_user.department == "Department of Math and Science":
            department1 = "DMS"
            req = AddingReq.objects.filter(Q(studID_id=data.studID) & (Q(subject_id__course=department1)))
            context = { 
                'current_user': current_user,
                'student_info': data,
                'req': req,
                'sched': sched
                }
        elif current_user.department == "Department of Liberal Arts":
            department1 = "DLA"
            req = AddingReq.objects.filter(Q(studID_id=data.studID) & (Q(subject_id__course=department1)))
            context = { 
                'current_user': current_user,
                'student_info': data,
                'req': req,
                'sched': sched
                }
        else: 
            context = { 
                'current_user': current_user,
                'student_info': data,
                'req': req,
                'sched': sched
                }
        return render(request, 'TupAssistApp/h-adding-edit.html', context)
    return redirect('/index') 

def h_edit_sub(request):
    studID = request.POST.get('studID')
    data = registration.objects.get(studID=studID)
    if request.method =='POST':
        id = request.POST.get('id')
        subject = request.POST.get('subject')
        section = request.POST.get('section')
        head_is_approve = request.POST.get('head_is_approve')
        head_remark = request.POST.get('head_remark')
        head_name = request.POST.get('head_name')
        head_date = datetime.now()   
        edit = AddingReq.objects.get(id=id) 
        edit.head_is_approve = request.POST.get('head_is_approve')
        edit.head_remark = request.POST.get('head_remark')
        edit.head_name = request.POST.get('head_name')
        edit.head_date = datetime.now()
        if request.POST.get('head_is_approve') == 'Approved':
            edit.admin_approve = 'Pending'
            edit.save()
            messages.success(request, 'Successfully edited the request!')
            content = 'Good day! \n\n' + head_name + " " + head_is_approve + 'd' + ' your request for ' + subject + ' ' + section + '\n\nRemarks: ' + head_remark
            send_mail('ADDING OF SUBJECT - REQUEST', 
            content, settings.EMAIL_HOST_USER , [data.email], fail_silently=False)
            return redirect('/h_adding_edit/'+ str(data.studID))
        else:
            edit.save()
            messages.success(request, 'Successfully edited the request!')
            content = 'Good day! \n\n' + head_name + " " + head_is_approve + 'd' + ' your request for ' + subject + ' ' + section + '\n\nRemarks: ' + head_remark
            send_mail('ADDING OF SUBJECT - REQUEST', 
            content, settings.EMAIL_HOST_USER , [data.email], fail_silently=False)
            return redirect('/h_adding_edit/'+ str(data.studID))

@login_required(login_url='/index')        
def h_dropping(request):
    if request.user.is_authenticated and request.user.userType == 'Department Head':
        current_user = request.user
        if current_user.department == "Department of Industrial Technology" or current_user.department == "Department of Engineering" or current_user.department == "Department of Industrial Education":
            test = registration.objects.filter(Q(department=current_user.department) & Q(userType='Student') & (Q(dropStatus='Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval')) | (Q(dropStatus='ADAA Approved')))
            cnt2 = len(AddingReq.objects.filter(Q(studID__department=current_user.department) & Q(head_is_approve='Pending')))
            context = { 
                'cnt2': cnt2,
                'test': test,
                'current_user': current_user
                }
        else:
            test = registration.objects.filter( Q(userType='Student') & (Q(dropStatus='Wait for Teacher, Department Head and Assist. Director of Academic Affairs Approval')) | (Q(dropStatus='ADAA Approved')))
            cnt2 = len(AddingReq.objects.filter(Q(studID__department=current_user.department) & Q(head_is_approve='Pending')))
            context = { 
                'cnt2': cnt2,
                'test': test,
                'current_user': current_user
                }
        return render(request, 'TupAssistApp/h-dropping.html', context)
    return redirect('/index') 

@login_required(login_url='/index')
def h_dropping_edit(request, studID):
    if request.user.is_authenticated and request.user.userType == 'Department Head':
        current_user = request.user
        data = registration.objects.get(studID=studID)
        sched = Schedule.objects.all()
        if current_user.department == "Department of Industrial Technology":
            department1 = "DIT"
            course1 = "BET-COET"
            req = DroppingReq.objects.filter(Q (studID_id=data.studID) & (Q(subject_id__course=department1) | (Q(subject_id__course=course1))))
            context = { 
                'current_user': current_user,
                'student_info': data,
                'req': req,
                'sched': sched
                }
        elif current_user.department == "Department of Industrial Education":
            department1 = "DIE"
            course1 = "BS-ICT"
            req = DroppingReq.objects.filter(Q(studID_id=data.studID) & (Q(subject_id__course=department1) | (Q(subject_id__course=course1))))
            context = { 
                'current_user': current_user,
                'student_info': data,
                'req': req,
                'sched': sched
                }
        elif current_user.department == "Department of Engineering":
            department1 = "DOE"
            course1 = "BSCE"
            req = DroppingReq.objects.filter(Q(studID_id=data.studID) & (Q(subject_id__course=department1) | (Q(subject_id__course=course1))))
            context = { 
                'current_user': current_user,
                'student_info': data,
                'req': req,
                'sched': sched
                }
        elif current_user.department == "Department of Math and Science":
            department1 = "DMS"
            req = DroppingReq.objects.filter(Q(studID_id=data.studID) & (Q(subject_id__course=department1)))
            context = { 
                'current_user': current_user,
                'student_info': data,
                'req': req,
                'sched': sched
                }
        elif current_user.department == "Department of Liberal Arts":
            department1 = "DLA"
            req = DroppingReq.objects.filter(Q(studID_id=data.studID) & (Q(subject_id__course=department1)))
            context = { 
                'current_user': current_user,
                'student_info': data,
                'req': req,
                'sched': sched
                }
        else: 
            context = { 
                'current_user': current_user,
                'student_info': data,
                'req': req,
                'sched': sched
                }
        return render(request, 'TupAssistApp/h_dropping_edit.html', context)
    return redirect('/index') 

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
        messages.success(request, 'Successfully edited the request!')
        return redirect('/h_dropping_edit/'+ str(data.studID))
 
@login_required(login_url='/index')
def h_transferring(request):
    if request.user.is_authenticated and request.user.userType == 'Department Head':
        current_user = request.user
        if current_user.department == "Department of Industrial Technology" or current_user.department == "Department of Engineering" or current_user.department == "Department of Industrial Education":
            test = registration.objects.filter(Q(department=current_user.department) & Q(userType='Student') & (Q(transferStatus='Wait for Department Head and Asst. Director for Academic Affairs Approval')) | Q(transferStatus='ADAA Approved'))
            cnt2 = len(AddingReq.objects.filter(Q(studID__department=current_user.department) & Q(head_is_approve='Pending')))
            context = { 
                'cnt2': cnt2,
                'test': test,
                'current_user': current_user
                }
        else:
            test = registration.objects.filter(Q(userType='Student') & (Q(transferStatus='Wait for Department Head and Asst. Director for Academic Affairs Approval')) | Q(transferStatus='ADAA Approved'))
            cnt2 = len(AddingReq.objects.filter(Q(studID__department=current_user.department) & Q(head_is_approve='Pending')))
            context = { 
                'cnt2': cnt2,
                'test': test,
                'current_user': current_user
                }
        return render(request, 'TupAssistApp/h-transferring.html', context)
    return redirect('/index') 

@login_required(login_url='/index')
def h_transferring_edit(request, studID):
    if request.user.is_authenticated and request.user.userType == 'Department Head':
        current_user = request.user
        data = registration.objects.get(studID=studID)
        req = TransferringReq.objects.filter(studID_id=data.studID)
        sched = Schedule.objects.all()
        if current_user.department == "Department of Industrial Technology":
            department1 = "DIT"
            course1 = "BET-COET"
            req = TransferringReq.objects.filter(Q (studID_id=data.studID) & (Q(subject_id__course=department1) | (Q(subject_id__course=course1))))
            context = { 
                'current_user': current_user,
                'student_info': data,
                'req': req,
                'sched': sched
                }
        elif current_user.department == "Department of Industrial Education":
            department1 = "DIE"
            course1 = "BS-ICT"
            req = TransferringReq.objects.filter(Q (studID_id=data.studID) & (Q(subject_id__course=department1) | (Q(subject_id__course=course1))))
            context = { 
                'current_user': current_user,
                'student_info': data,
                'req': req,
                'sched': sched
                }
        elif current_user.department == "Department of Engineering":
            department1 = "DOE"
            course1 = "BSCE"
            req = TransferringReq.objects.filter(Q (studID_id=data.studID) & (Q(subject_id__course=department1) | (Q(subject_id__course=course1))))
            context = { 
                'current_user': current_user,
                'student_info': data,
                'req': req,
                'sched': sched
                }
        elif current_user.department == "Department of Math and Science":
            department1 = "DMS"
            req = TransferringReq.objects.filter(Q(studID_id=data.studID) & (Q(subject_id__course=department1)))
            context = { 
                'current_user': current_user,
                'student_info': data,
                'req': req,
                'sched': sched
                }
        elif current_user.department == "Department of Liberal Arts":
            department1 = "DLA"
            req = TransferringReq.objects.filter(Q(studID_id=data.studID) & (Q(subject_id__course=department1)))
            context = { 
                'current_user': current_user,
                'student_info': data,
                'req': req,
                'sched': sched
                }
        else: 
            context = { 
                'current_user': current_user,
                'student_info': data,
                'req': req,
                'sched': sched
                }
        return render(request, 'TupAssistApp/h-transferring-edit.html', context)
    return redirect('/index') 

def h_edit_sub2(request):
    studID = request.POST.get('studID')
    data = registration.objects.get(studID=studID)
    if request.method =='POST':
        id = request.POST.get('id')   
        edit = TransferringReq.objects.get(id=id) 
        edit.head_is_approve = request.POST.get('head_is_approve')
        edit.head_remark = request.POST.get('head_remark')
        edit.head_name = request.POST.get('head_name')
        edit.head_date = datetime.now()
        edit.save()
        messages.success(request, 'Successfully edited the request!')
        return redirect('/h_transferring_edit/'+ str(data.studID))