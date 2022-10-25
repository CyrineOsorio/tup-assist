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
    email = models.CharField(max_length=255, null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    course = models.CharField(max_length=255, null=True, blank=True)
    yrandsec = models.CharField(max_length=255, null=True, blank=True)
    sched = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "AddingReq" 


class DroppingReq(models.Model):
    email = models.CharField(max_length=255, null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    course = models.CharField(max_length=255, null=True, blank=True)
    yrandsec = models.CharField(max_length=255, null=True, blank=True)
    sched = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "DroppingReq" 

class TransferringReq(models.Model):
    email = models.CharField(max_length=255, null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    course = models.CharField(max_length=255, null=True, blank=True)
    yrandsec = models.CharField(max_length=255, null=True, blank=True)
    sched = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "TransferringReq" 


# Student Registration and Student account refernce for tupcavite gsfe account only
class registration(AbstractUser):
    yrandsec = [
        ('1A', '1A'),
        ('2A', '2A'),
        ('3A', '3A'),
        ('4A', '4A'),
        ('1B', '1B'),
        ('2B', '2B'),
        ('3B', '3B'),
        ('4B', '4B'),
    ]
    userType = [
        ('STDNT', 'Student'),
        ('DH', 'Department Head'),
        ('PIC', 'Person-in-charge'),
        ('R', 'Registrar'),
    ]

    # FOR STUDENT AND PIC
    course = [
        ('BET-ET', 'Electrical Technology'),
        ('BET-ESET', 'Electronics Technology'),
        ('BET-COET', 'Computer Engineering Technology '),
        ('BET-CT', 'Civil Technology'),
        ('BET-MT', 'Mechanical Technology'),
        ('BET-AT', 'Automotive Technology'),
        ('BET-PPT', 'Power Plant Technology'),
    ]

    # FOR DEPARTMENT HEAD
    department = [
        ('Department of Industrial Technology', 'Department of Industrial Technology'),
        ('Department of Industial Education', 'Department of Industial Education'),
        ('Department of Engineering', 'Department of Engineering'),
    ]
    
    email = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    course = models.CharField(max_length=255, choices= course, null=True, blank=True)
    yrandsec = models.CharField(max_length=255, choices= yrandsec, null=True, blank=True)
    studID = models.CharField(max_length=255, null=True, blank=True)
    userType = models.CharField(max_length=255, choices= userType, verbose_name='userType', default ='STDNT')
    department = models.CharField(max_length=255, choices= department, verbose_name='department', null=True)


    class Meta:
        verbose_name_plural = "registration" 



class StudentReference(models.Model):
    email = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "StudentReference" 