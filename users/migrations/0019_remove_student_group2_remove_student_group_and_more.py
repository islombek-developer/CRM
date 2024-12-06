# Generated by Django 5.1.1 on 2024-12-04 12:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_remove_student_group_remove_student_group2_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='group2',
        ),
        migrations.RemoveField(
            model_name='student',
            name='group',
        ),
        migrations.AddField(
            model_name='student',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students_group', to='users.group'),
        ),
    ]