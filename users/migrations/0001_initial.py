# Generated by Django 5.1.1 on 2024-11-24 05:03

import datetime
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('image', models.ImageField(blank=True, default='profile_pics/default.jpg', null=True, upload_to='profile_pics/')),
                ('phone_number', models.CharField(blank=True, max_length=13, null=True)),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
                ('jobs', models.CharField(blank=True, max_length=200, null=True)),
                ('user_role', models.CharField(choices=[('teacher', 'teacher'), ('admin', 'admin')], default='teacher', max_length=100)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('week_days', models.CharField(choices=[('even', 'Juft kunlar'), ('odd', 'Toq kunlar'), ('mon_wed_fri', 'Dushanba/Chorshanba/Juma'), ('tue_thu_sat', 'Seshanba/Payshanba/Shanba')], default='even', max_length=20)),
                ('monthly_payment', models.IntegerField(default=200000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='days', to='users.group')),
            ],
            options={
                'ordering': ['-date'],
                'unique_together': {('group', 'date')},
            },
        ),
        migrations.CreateModel(
            name='Month',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.CharField(max_length=150)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='month', to='users.group')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students', to='users.group')),
            ],
        ),
        migrations.CreateModel(
            name='DailyPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_date', models.DateField(default=datetime.date.today)),
                ('monthly_fee', models.IntegerField(default=200000)),
                ('remaining_amount', models.IntegerField()),
                ('paid_amount', models.IntegerField()),
                ('note', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_payments', to='users.group')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_payments', to='users.student')),
            ],
            options={
                'ordering': ['-payment_date'],
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of', models.DateField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('homework_status', models.BooleanField(default=False)),
                ('lesson_file', models.FileField(blank=True, null=True, upload_to='lesson/')),
                ('video', models.FileField(blank=True, null=True, upload_to='video/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp4', 'mp3', 'AVI', 'WMV'])])),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson', to='users.group')),
            ],
            options={
                'unique_together': {('team', 'title')},
            },
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('date', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.day')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance', to='users.group')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.student')),
            ],
            options={
                'ordering': ['-date__date'],
                'unique_together': {('student', 'date')},
            },
        ),
    ]
