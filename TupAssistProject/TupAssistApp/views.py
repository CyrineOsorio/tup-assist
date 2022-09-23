from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import redirect, render
#from pyexpat.errors import messages
from django.contrib import messages

from .models import *
# Create your views here.
installed_apps = ['TupAssistApp']


#LOGIN PAGE
def index(request):
    return render(request, 'TupAssistApp/index.html')

def student(request):
    return render(request, 'TupAssistApp/student.html')

def registrar(request):
    return render(request, 'TupAssistApp/registrar.html')