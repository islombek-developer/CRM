# Generated by Django 5.1.1 on 2024-12-06 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_remove_student_date_of_remove_user_date_of_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='week_days',
            field=models.CharField(choices=[('toq_kunlari', 'Dushanba/Chorshanba/Juma'), ('juft_kunlari', 'Seshanba/Payshanba/Shanba'), ('INDUVIDUAL', 'INDUVIDUAL')], default='toq_kunlari', max_length=20),
        ),
    ]