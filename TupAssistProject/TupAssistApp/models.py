from django.db import models

# Create your models here.

class Subjects(models.Model):           
    SubCode = models.CharField(max_length=255)
    SubName = models.CharField(max_length=255)
    Course = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Subjects"

class TransStatus(models.Model):
    TransName = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)  

    class Meta:
        verbose_name_plural = "TransStatus"   