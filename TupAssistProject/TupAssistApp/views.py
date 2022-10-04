from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import redirect, render
#from pyexpat.errors import messages
from django.contrib import messages

from .models import *

import csv
import pandas
# Create your views here.
installed_apps = ['TupAssistApp']


#LOGIN PAGE
def index(request):
    return render(request, 'TupAssistApp/index.html')

def student(request):
    return render(request, 'TupAssistApp/student.html')

def registrar(request):
    subs = Subjects.objects.all()
    context={
        'subs': subs
    }
    return render(request, 'TupAssistApp/registrar.html', context)


def sub_cvs(request):
    if request.method=='POST':
        with open('TupAssistApp/csv/subject.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                new_revo = Subjects.objects.create(SubCode=row['SubCode'], SubName=row['SubName'], Course=row['Course'])
                new_revo.save()
            return redirect('/registrar')

   