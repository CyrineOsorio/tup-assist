from django.db import models

# Create your models here.

class Subjects(models.Model):           
    SubCode = models.CharField(max_length=255)
    SubName = models.CharField(max_length=255)
    Course = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Subjects"