# Generated by Django 5.1.1 on 2024-12-01 06:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_dailypayment_amount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dailypayment',
            name='amount',
        ),
    ]