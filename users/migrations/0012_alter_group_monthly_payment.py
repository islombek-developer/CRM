# Generated by Django 5.1.1 on 2024-12-02 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_student_phone2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='monthly_payment',
            field=models.IntegerField(),
        ),
    ]