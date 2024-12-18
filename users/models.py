from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum
from django.core.validators import MaxValueValidator,FileExtensionValidator
from datetime import datetime, date,timedelta,timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum

class User(AbstractUser):
    USER_ROLE =(
        ('teacher','teacher'),
        ('admin','admin'),
    )
    image = models.ImageField(upload_to='profile_pics/', blank=True, null=True, default='profile_pics/default.jpg')
    phone_number = models.CharField(max_length=13, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    jobs = models.CharField(max_length=200, blank=True, null=True)
    user_role = models.CharField(max_length=100,choices=USER_ROLE,default="teacher")


class Teacher(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    date_of = models.DateField(null=True,blank=True )

    
    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return self.get_full_name()




class WeekDayChoices(models.TextChoices):
    MON_WED_FRI = 'toq_kunlari', 'Dushanba/Chorshanba/Juma'
    TUE_THU_SAT = 'juft_kunlari', 'Seshanba/Payshanba/Shanba'
    INDUVIDUAL = 'INDUVIDUAL','INDUVIDUAL'


class Group(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL,null=True)
    week_days = models.CharField(
        max_length=20,
        choices=WeekDayChoices.choices,
        default=WeekDayChoices.MON_WED_FRI
    )
    monthly_payment = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

    @property
    def student_count(self):
        return self.students.count()

    @property
    def group_count(self):
        return self.groups.count()

    @property
    def total_payment_status(self):
        total = 0
        for student in self.students.all():
            payment = student.monthlypayments.aggregate(total=Sum('oylik'))['total'] or 0
            total += payment - (200000) 
        return total



    @property
    def total_remaining(self):
        return DailyPayment.get_group_total_remaining(self.id)

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15,null=True,blank=True)
    phone2 = models.CharField(max_length=15,null=True,blank=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def attendance_percentage(self):
        if not self.group:
            return 0
        
        all_attendances = Attendance.objects.filter(student=self)
        if not all_attendances.exists():
            return 0
        total_days = all_attendances.count()
        present_days = all_attendances.filter(status=True).count()
        return (present_days / total_days) * 100 if total_days > 0 else 0
    
    @property
    def remaining_payment(self):
        latest_payment = DailyPayment.objects.filter(
            student=self
        ).order_by('-payment_date').first()
        
        return latest_payment.remaining_amount if latest_payment else latest_payment

    def daily_payment_calculation(self):

        if not self.group:
            return 0

        daily_payment = self.group.monthly_payment / 30
        daily_payment_obj, created = DailyPayment.objects.get_or_create(
            student=self,
            defaults={
                'daily_amount': daily_payment,
                'remaining_amount': self.group.monthly_payment
            }
        )

        current_time = timezone.now()
        if not created and (current_time - daily_payment_obj.last_payment_date).days >= 1:
         
            daily_payment_obj.remaining_amount -= daily_payment
            if daily_payment_obj.remaining_amount <= 0:
                daily_payment_obj.remaining_amount = self.group.monthly_payment
                daily_payment_obj.last_reset_date = current_time
            
            daily_payment_obj.last_payment_date = current_time
            daily_payment_obj.save()

        return daily_payment_obj.remaining_amount



    @property
    def total_remaining(self):
        return DailyPayment.get_group_total_remaining(self.id)


from django.utils import timezone
from datetime import date, timedelta

class Attendance(models.Model):
    group = models.ForeignKey(
        Group, 
        on_delete=models.SET_NULL, 
        related_name='attendances',null=True
    )
    student = models.ForeignKey(
        Student, 
        on_delete=models.SET_NULL, 
        related_name='attendances',null=True
    )
    date = models.DateField(default=timezone.localdate)
    status = models.BooleanField(default=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'group', 'date']
        ordering = ['-date']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'

    def __str__(self):
        status_text = "Keldi" if self.status else "Kelmadi"
        return f"{self.student.full_name} - {self.date} - {status_text}"

    @property
    def month(self):
        return self.date.strftime('%B')

    @property
    def day_of_month(self):
        return self.date.day

    @classmethod
    def create_days_for_month(cls, group, year, month):
 
        start_date = date(year, month, 1)
        
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        current_date = start_date
        created_dates = []
        
        while current_date <= end_date:
            should_create = False
            
            if group.week_days == WeekDayChoices.MON_WED_FRI and current_date.weekday() in [0, 2, 4]:
                should_create = True
            elif group.week_days == WeekDayChoices.TUE_THU_SAT and current_date.weekday() in [1, 3, 5]:
                should_create = True
        
            if should_create:
                students = group.students.all()
                for student in students:
                    cls.objects.get_or_create(
                        group=group, 
                        student=student, 
                        date=current_date,
                        defaults={'status': False}  
                    )
                created_dates.append(current_date)
            
            current_date += timedelta(days=1)
        
        return created_dates

    def save(self, *args, **kwargs):
        existing = Attendance.objects.filter(
            student=self.student, 
            group=self.group, 
            date=self.date
        ).exclude(pk=self.pk)
        
        if existing.exists():
            raise ValueError("An attendance record for this student, group, and date already exists.")
        
        super().save(*args, **kwargs)




class DailyPayment(models.Model):
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, related_name='daily_payments',null=True)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, related_name='daily_payments',null=True)
    payment_date = models.DateField(default=date.today)
    monthly_fee = models.IntegerField(default=200000)
    remaining_amount = models.IntegerField()
    paid_amount = models.IntegerField()
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.payment_date} - {self.paid_amount}"

    def save(self, *args, **kwargs):
        current_month = timezone.now().month
        current_year = timezone.now().year
        last_payment = DailyPayment.objects.filter(student=self.student).order_by('-payment_date').first()

        if self.group and self.group.monthly_payment:
            monthly_payment = self.group.monthly_payment
        else:
            monthly_payment = self.monthly_fee 

        if not self.pk:  # New record
            if last_payment:
                last_month = last_payment.payment_date.month
                last_year = last_payment.payment_date.year

                if last_month != current_month or last_year != current_year:
                    self.remaining_amount = monthly_payment - self.paid_amount
                else:
                    self.remaining_amount = last_payment.remaining_amount - self.paid_amount
            else:
                self.remaining_amount = monthly_payment - self.paid_amount
        else:  # Updating an existing record
            if self.payment_date.month != last_payment.payment_date.month:
                self.remaining_amount = monthly_payment - self.paid_amount
            else:
                self.remaining_amount = last_payment.remaining_amount - self.paid_amount

        # Ensure remaining_amount does not go below 0
        if self.remaining_amount < 0:
            self.remaining_amount = 0

        # If fully paid, set remaining_amount to 0
        total_paid = DailyPayment.objects.filter(
            student=self.student,
            group=self.group
        ).aggregate(total_paid=models.Sum('paid_amount'))['total_paid'] or 0

        if total_paid >= monthly_payment:
            self.remaining_amount = 0

        super().save(*args, **kwargs)

    @classmethod
    def get_student_balance(cls, student_id):
        """Returns the current balance for the given student."""
        latest_payment = cls.objects.filter(
            student_id=student_id
        ).order_by('-payment_date').first()

        student = Student.objects.get(id=student_id)
        group_monthly_fee = student.group.monthly_payment if student.group else cls._meta.get_field('monthly_payment').default

        if not latest_payment:
            return group_monthly_fee  # Use group's monthly fee

        return latest_payment.remaining_amount


    @classmethod
    def get_group_total_remaining(cls, group_id):
        """Returns the total remaining amount for a group."""
        group = Group.objects.get(id=group_id)
        group_monthly_fee = group.monthly_payment

        latest_payments = cls.objects.filter(
            group_id=group_id   
        ).values('student').annotate(
            latest_date=models.Max('payment_date')
        )

        total_remaining = 0
        for payment in latest_payments:
            student_latest = cls.objects.filter(
                student_id=payment['student'],
                payment_date=payment['latest_date']
            ).first()
            if student_latest:
                total_remaining += student_latest.remaining_amount
            else:
                total_remaining += group_monthly_fee  # Use group's monthly fee for unpaid students

        students_in_group = Student.objects.filter(group_id=group_id)
        paid_students = [payment['student'] for payment in latest_payments]
        unpaid_students = students_in_group.exclude(id__in=paid_students)

        for student in unpaid_students:
            total_remaining += group_monthly_fee

        return total_remaining

    @classmethod
    def get_total_payments_across_all_groups(cls):
        """Hamma guruhdagi o‘quvchilarning jami to‘lovlarini hisoblaydi."""
        total_paid = 0

        for group in Group.objects.all():
            for student in group.students.all():
                total_paid += student.daily_payments.aggregate(total=Sum('paid_amount'))['total'] or 0

        return total_paid



class Month(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='month')
    month = models.CharField(max_length=150)

    def __str__(self) -> str:
        return f"{self.month} "




class Lesson(models.Model):
    team = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='lesson')
    title = models.CharField(max_length=100, unique=True)
    date = models.DateField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    homework_status = models.BooleanField(default=False)
    lesson_file = models.FileField(upload_to='lesson/',  null=True,blank=True)
    video = models.FileField(
        upload_to='video/', 
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mp3', 'AVI', 'WMV'])],
        null=True,
        blank=True
    )


    class Meta:
        unique_together = ['team', 'title']

    def __str__(self):
        return self.title