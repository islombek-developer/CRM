# Generated by Django 5.1.1 on 2024-12-06 12:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_rename_monthly_payment_group_monthly_fee'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='monthly_fee',
            new_name='monthly_payment',
        ),
    ]
