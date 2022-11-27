from email.policy import default
from django.db import models
from django.db.models import Model
import os
from django.contrib.auth.models import AbstractUser

# Student Registration and Student account refernce for tupcavite gsfe account only
class registration(AbstractUser):
    userType = [
        ('Student', 'Student'),
        ('Department Head', 'Department Head'),
        ('Person-in-charge', 'Person-in-charge'), 
        ('Teacher', 'Teacher'), 
    ]
    department = [
        ('Department of Industrial Technology', 'Department of Industrial Technology'),
        ('Department of Industrial Education', 'Department of Industrial Education'),
        ('Department of Engineering', 'Department of Engineering'),
        ('Department of Math and Science', 'Department of Math and Science'),
        ('Department of Liberal Arts', 'Department of Liberal Arts'),
    ]
    section = [
        ('A', 'A'),
        ('B', 'B'),
    ]
    studID = models.BigAutoField(primary_key=True)
    course = models.CharField(max_length=255, null=True, blank=True)
    year = models.IntegerField(blank=True, null=True)
    section = models.CharField(max_length=255, choices= section, null=True, blank=True)
    userType = models.CharField(max_length=255, choices= userType, verbose_name='userType', null=True)
    department = models.CharField(max_length=255, choices= department, verbose_name='department', null=True)
    upload = models.FileField(upload_to ='grades/', null=True, blank=True)
    addStatus = models.CharField(max_length=255, blank=True)
    dropStatus = models.CharField(max_length=255, blank=True)
    transferStatus = models.CharField(max_length=255, blank=True)
    
    

    class Meta:
        verbose_name_plural = "registration" 

# Transaction json file to import | code in terminal: python manage.py loaddata data.json
class TransStatus(models.Model):
    TransName = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    school_year = models.IntegerField(null=True, blank=True)
    semester = models.IntegerField(null=True, blank=True)


    class Meta:
        verbose_name_plural = "TransStatus" 

# CvS file of subjects to import in Subjects Model
class Subjects(models.Model):           
    course = models.CharField(max_length=255)
    year = models.IntegerField()
    semester = models.IntegerField()
    shop = models.IntegerField()
    is_lab = models.CharField(max_length=255, null=True, blank=True, default="L")
    description = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Subjects" 

# CvS file of schedule to import in Schedule Model
class Schedule(models.Model):
    gSheetLink = models.CharField(max_length=500, null=True, blank=True)
    school_year = models.IntegerField(blank=True, null=True)
    semester = models.IntegerField(blank=True, null=True)
    department = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Schedule" 


# Model for Student Adding Transaction
class AddingReq(models.Model):
    studID = models.ForeignKey("registration", on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, null=True, blank=True)
    section = models.CharField(max_length=255, null=True, blank=True)
    sched = models.CharField(max_length=255, null=True, blank=True)
    pic_is_approve = models.CharField(max_length=255, null=True, blank=True, default='Pending')
    pic_remark = models.CharField(max_length=255, null=True, blank=True)
    pic_name = models.CharField(max_length=255, null=True, blank=True)
    pic_date = models.DateTimeField(null=True, blank=True)
    head_is_approve = models.CharField(max_length=255, null=True, blank=True)
    head_remark = models.CharField(max_length=255, null=True, blank=True)
    head_name = models.CharField(max_length=255, null=True, blank=True)
    head_date = models.DateTimeField(null=True, blank=True)
    admin_approve = models.CharField(max_length=255, null=True, blank=True)
    admin_name = models.CharField(max_length=255, null=True, blank=True)
    admin_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "AddingReq" 


class DroppingReq(models.Model):
    studID = models.ForeignKey("registration", on_delete=models.CASCADE)
    subject = models.CharField(max_length=255, null=True, blank=True)
    section = models.CharField(max_length=255, null=True, blank=True)
    sched = models.CharField(max_length=255, null=True, blank=True)
    subj_teacher_approve = models.CharField(max_length=255, null=True, blank=True, default='Pending')
    subj_teacher_remark = models.CharField(max_length=255, null=True, blank=True)
    subj_teacher_name = models.CharField(max_length=255, null=True, blank=True)
    subj_teacher_date = models.DateTimeField(null=True, blank=True)
    head_is_approve = models.CharField(max_length=255, null=True, blank=True)
    head_remark = models.CharField(max_length=255, null=True, blank=True)
    head_name = models.CharField(max_length=255, null=True, blank=True)
    head_date = models.DateTimeField(null=True, blank=True)
    admin_approve = models.CharField(max_length=255, null=True, blank=True)
    admin_name = models.CharField(max_length=255, null=True, blank=True)
    admin_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "DroppingReq" 

class TransferringReq(models.Model):
    studID = models.ForeignKey("registration", on_delete=models.CASCADE)  
    subject = models.CharField(max_length=255, null=True, blank=True)
    section = models.CharField(max_length=255, null=True, blank=True)
    sched = models.CharField(max_length=255, null=True, blank=True)
    subj_teacher_approve = models.CharField(max_length=255, null=True, blank=True, default='Pending')
    subj_teacher_remark = models.CharField(max_length=255, null=True, blank=True)
    subj_teacher_name = models.CharField(max_length=255, null=True, blank=True)
    subj_teacher_date = models.DateTimeField(null=True, blank=True)
    head_is_approve = models.CharField(max_length=255, null=True, blank=True)
    head_remark = models.CharField(max_length=255, null=True, blank=True)
    head_name = models.CharField(max_length=255, null=True, blank=True)
    head_date = models.DateTimeField(null=True, blank=True)
    admin_approve = models.CharField(max_length=255, null=True, blank=True)
    admin_name = models.CharField(max_length=255, null=True, blank=True)
    admin_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "TransferringReq" 