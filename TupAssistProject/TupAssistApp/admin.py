from django.contrib import admin

from .models import registration, Subjects, AddingReq, DroppingReq, Schedule, TransferringReq, TransStatus


# Register your models here.
# https://docs.djangoproject.com/en/1.8/intro/tutorial02/
admin.site.register(registration)
admin.site.register(Subjects)
admin.site.register(AddingReq)
admin.site.register(DroppingReq)
admin.site.register(Schedule)
admin.site.register(TransferringReq)
admin.site.register(TransStatus)