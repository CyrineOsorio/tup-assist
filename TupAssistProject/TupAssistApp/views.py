from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import redirect, render
#from pyexpat.errors import messages
from django.contrib import messages

from .models import *

import csv

import os

import easygui


# Create your views here.
installed_apps = ['TupAssistApp']


#LOGIN PAGE
def index(request):
    return render(request, 'TupAssistApp/index.html')

def student(request):
    return render(request, 'TupAssistApp/student.html')

def registrar(request):
    subs = Subjects.objects.all()
    status = TransStatus.objects.all()
    sched = Schedule.objects.latest('id')
    # latest_sched = sched.gSheetLink
    # print(latest_sched)
    context = {
        'subs': subs,
        'sched': sched
    }
    return render(request, 'TupAssistApp/registrar.html', context)


def sub_cvs(request):
    if request.method=='POST': 
        file = easygui.fileopenbox()
        print(file)
        with open(file) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                new_revo = Subjects.objects.create(SubCode=row['SubCode'], SubName=row['SubName'], Course=row['Course'])
                new_revo.save()
            return redirect('/registrar')
    return redirect('/registrar')

def import_sched(request):
    if request.method=='POST': 
        gSheetLink = request.POST.get('gSheetLink')
        year = request.POST.get('year')
        semester = request.POST.get('semester')
        status = request.POST.get('status')
        data = Schedule.objects.create(gSheetLink = gSheetLink, year = year, semester = semester, status = status)
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
    