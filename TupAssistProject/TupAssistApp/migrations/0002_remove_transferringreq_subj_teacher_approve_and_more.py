# Generated by Django 4.1.2 on 2023-01-03 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('TupAssistApp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transferringreq',
            name='subj_teacher_approve',
        ),
        migrations.RemoveField(
            model_name='transferringreq',
            name='subj_teacher_date',
        ),
        migrations.RemoveField(
            model_name='transferringreq',
            name='subj_teacher_name',
        ),
        migrations.RemoveField(
            model_name='transferringreq',
            name='subj_teacher_remark',
        ),
    ]