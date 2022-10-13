from email.policy import default
from django.db import models
from django.db.models import Model
import os
from django.contrib.auth.models import AbstractUser

# Create your models here.

# CvS file of subjects to import in Subjects Model
class Subjects(models.Model):           
    SubCode = models.CharField(max_length=255)
    SubName = models.CharField(max_length=255)
    Course = models.CharField(max_length=255)
    Units = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Subjects"

# Transaction json file to import | code in terminal: python manage.py loaddata data.json
class TransStatus(models.Model):
    TransName = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)  

    class Meta:
        verbose_name_plural = "TransStatus"  

# CvS file of schedule to import in Schedule Model
class Schedule(models.Model):
    gSheetLink = models.CharField(max_length=500, null=True, blank=True)
    year = models.IntegerField(blank=True, null=True)
    semester = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Schedule" 

# Model for Student Adding Transaction
class AddingReq(models.Model):
    subcode = models.CharField(max_length=255, null=True, blank=True)
    subname = models.CharField(max_length=255, null=True, blank=True)
    course = models.CharField(max_length=255, null=True, blank=True)
    yrandsec = models.CharField(max_length=255, null=True, blank=True)
    sched = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "AddingReq" 


# Student Registration and Student account refernce for tupcavite gsfe account only
class registration(AbstractUser):
    yrandsec = [
        ('BET-COET-S-1A', 'BET-COET-S-1A'),
        ('BET-COET-NS-1B', 'BET-COET-NS-1B'),
        ('BET-COET-S-2A', 'BET-COET-S-2A'),
        ('BET-COET-NS-2B', 'BET-COET-NS-2B'),
        ('BET-COET-S-3A', 'BET-COET-S-3A'),
        ('BET-COET-NS-3B', 'BET-COET-NS-3B'),
        ('BET-COET-S-4A', 'BET-COET-S-4A'),
        ('BET-COET-NS-4B', 'BET-COET-NS-4B'),
    ]
    userType = [
        ('STDNT', 'Student'),
        ('DH', 'Department Head'),
        ('PIC', 'Person-in-charge'),
    ]
    email = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    course = models.CharField(max_length=255, null=True, blank=True)
    yrandsec = models.CharField(max_length=255, null=True, blank=True)
    studID = models.CharField(max_length=255, null=True, blank=True)
    userType = models.CharField(max_length=255, choices= userType, verbose_name='userType', default ='STDNT')

    class Meta:
        verbose_name_plural = "registration" 

class StudentReference(models.Model):
    email = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "StudentReference" 