from django.contrib import admin

from .models import registration, Subjects


# Register your models here.
# https://docs.djangoproject.com/en/1.8/intro/tutorial02/
admin.site.register(registration)
admin.site.register(Subjects)
