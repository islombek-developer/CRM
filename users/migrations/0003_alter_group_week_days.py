# Generated by Django 5.1.1 on 2024-11-24 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_group_week_days'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='week_days',
            field=models.CharField(choices=[('toq_kunlari', 'Dushanba/Chorshanba/Juma'), ('juft_kunlari', 'Seshanba/Payshanba/Shanba')], default='toq_kunlari', max_length=20),
        ),
    ]
