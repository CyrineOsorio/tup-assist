from email.policy import default
from django.db import models
from django.db.models import Model
import os
from django.contrib.auth.models import AbstractUser

# Transaction json file to import | code in terminal: python manage.py loaddata data.json
class TransStatus(models.Model):
    TransName = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)  

    class Meta:
        verbose_name_plural = "TransStatus" 

# CvS file of subjects to import in Subjects Model
class Subjects(models.Model):           
    subject_code = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Subjects" 

# CvS file of schedule to import in Schedule Model
class Schedule(models.Model):
    gSheetLink = models.CharField(max_length=500, null=True, blank=True)
    school_year = models.IntegerField(blank=True, null=True)
    semester = models.IntegerField(blank=True, null=True)
    section = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Schedule" 

class StudentReference(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    section = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "StudentReference" 


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
        ('DH', 'Department Head'),
        ('Person-in-charge', 'Person-in-charge'),
    ]  

    # FOR STUDENT AND PIC
    course = [
        ('BGT-AT', 'Bachelor in Graphics Technology major in Architecture Technology'),
        ('BET-ET', 'Bachelor of Engineering Technology major in Electrical Technology'),
        ('BET-ESET', 'Bachelor of Engineering Technology major in Electronics Technology Track: Industrial Automation Technology'),
        ('BET-COET', 'Bachelor of Engineering Technology major in Computer Engineering Technology'),
        ('BET-CT', 'Bachelor of Engineering Technology major in Contruction Technology'),
        ('BET-CT', 'Bachelor of Engineering Technology major in Civil Technology'),
        ('BET-MT', 'Bachelor of Engineering Technology major in Mechanical Technology'),
        ('BET-AT', 'Bachelor of Engineering Technology major in Mechanical Engineering Technology Track: Automotive Technology'),
        ('BET-PPT', 'Bachelor of Engineering Technology major in Mechanical Engineering Technology Track: Power Plant Technology'),
        ('BSIE-HE', 'Bachelor of Science in Industrial Education major in: Home Economics'),
        ('BSIE-IA', 'Bachelor of Science in Industrial Education major in: Industrial Arts'),
        ('BSIE-ICT', 'Bachelor of Science in Industrial Education major in: Information and Communication Technology'),
        ('BTTE-CP', 'Bachelor of Technical Vocational Teacher Education major in: Computer Programming'),
        ('BTTE-EL', 'Bachelor of Technical Vocational Teacher Education major in: Electrical'),
        ('BSCE', 'Bachelor of Science in Civil Engineering'),
        ('BSEE', 'Bachelor of Science in Electrical Engineering'),
        ('BSME', 'Bachelor of Science in Mechanical Engineering'),
    ]

    # FOR DEPARTMENT HEAD
    department = [
        ('Department of Industrial Technology', 'Department of Industrial Technology'),
        ('Department of Industrial Education', 'Department of Industrial Education'),
        ('Department of Engineering', 'Department of Engineering'),
    ]
    id = models.BigAutoField(primary_key=True)
    studID = models.IntegerField(blank=True, null=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    course = models.CharField(max_length=255, choices= course, null=True, blank=True)
    yrandsec = models.CharField(max_length=255, choices= yrandsec, null=True, blank=True)
    userType = models.CharField(max_length=255, choices= userType, verbose_name='userType', null=True)
    department = models.CharField(max_length=255, choices= department, verbose_name='department', null=True)
    upload = models.FileField(upload_to ='grades/', null=True, blank=True)
    addStatus = models.CharField(max_length=255, blank=True)
    dropStatus = models.CharField(max_length=255, blank=True)
    transferStatus = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name_plural = "registration" 


# Model for Student Adding Transaction
class AddingReq(models.Model):
    studID = models.IntegerField()
    subject = models.CharField(max_length=255, null=True, blank=True)
    section = models.CharField(max_length=255, null=True, blank=True)
    sched = models.CharField(max_length=255, null=True, blank=True)
    pic_is_approve = models.CharField(max_length=255, null=True, blank=True, default='Pending')
    pic_remark = models.CharField(max_length=255, null=True, blank=True)
    pic_name = models.CharField(max_length=255, null=True, blank=True)
    pic_date = models.DateTimeField()
    head_is_approve = models.BooleanField(default=False)
    head_remark = models.CharField(max_length=255, null=True, blank=True)
    head_name = models.CharField(max_length=255, null=True, blank=True)
    head_date = models.DateTimeField()
    
    class Meta:
        verbose_name_plural = "AddingReq" 


class DroppingReq(models.Model):
    studID = models.IntegerField()
    
    
    class Meta:
        verbose_name_plural = "DroppingReq" 

class TransferringReq(models.Model):
    studID = models.IntegerField()
    
    class Meta:
        verbose_name_plural = "TransferringReq" 