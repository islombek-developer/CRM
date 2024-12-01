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

    def __str__(self):
        return self.user.username




class WeekDayChoices(models.TextChoices):
    MON_WED_FRI = 'toq_kunlari', 'Dushanba/Chorshanba/Juma'
    TUE_THU_SAT = 'juft_kunlari', 'Seshanba/Payshanba/Shanba'


class Group(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    week_days = models.CharField(
        max_length=20,
        choices=WeekDayChoices.choices,
        default=WeekDayChoices.MON_WED_FRI
    )
    monthly_payment = models.IntegerField(default=200000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

    @property
    def student_count(self):
        """Guruhdagi o‘quvchilar sonini hisoblaydi."""
        return self.students.count()

    @property
    def group_count(self):
        return self.groups.count()

    @property
    def total_payment_status(self):
        """Guruhdagi o‘quvchilarning umumiy oylik to‘lovlarini hisoblaydi."""
        total = 0
        for student in self.students.all():
            # Talabaning jami oylik to‘lovini olamiz
            payment = student.monthlypayments.aggregate(total=Sum('oylik'))['total'] or 0
            total += payment - (200000) 
        return total



    @property
    def total_remaining(self):
        return DailyPayment.get_group_total_remaining(self.id)

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
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
        # Check if group exists to avoid errors
        if not self.group:
            return 0
        
        # Get all attendance records for this student
        all_attendances = Attendance.objects.filter(student=self)
        
        # If no attendances, return 0
        if not all_attendances.exists():
            return 0
        
        # Total possible attendance days (based on group's days)
        total_days = all_attendances.count()
        
        # Count of present days
        present_days = all_attendances.filter(status=True).count()
        
        # Calculate percentage
        return (present_days / total_days) * 100 if total_days > 0 else 0
    
    @property
    def remaining_payment(self):
        latest_payment = DailyPayment.objects.filter(
            student=self
        ).order_by('-payment_date').first()
        
        return latest_payment.remaining_amount if latest_payment else 200000

    def daily_payment_calculation(self):

        if not self.group:
            return 0

        daily_payment = self.group.monthly_payment / 30

        # Get or create daily payment record
        daily_payment_obj, created = DailyPayment.objects.get_or_create(
            student=self,
            defaults={
                'daily_amount': daily_payment,
                'remaining_amount': self.group.monthly_payment
            }
        )

        # Check if 24 hours have passed since last payment
        current_time = timezone.now()
        if not created and (current_time - daily_payment_obj.last_payment_date).days >= 1:
            # Subtract daily payment
            daily_payment_obj.remaining_amount -= daily_payment
            
            # If remaining amount is less than or equal to zero, reset to full amount
            if daily_payment_obj.remaining_amount <= 0:
                daily_payment_obj.remaining_amount = self.group.monthly_payment
                daily_payment_obj.last_reset_date = current_time
            
            daily_payment_obj.last_payment_date = current_time
            daily_payment_obj.save()

        return daily_payment_obj.remaining_amount



    @property
    def total_remaining(self):
        return DailyPayment.get_group_total_remaining(self.id)

from django.db import models
from django.utils import timezone
from datetime import date, timedelta

class Attendance(models.Model):
    group = models.ForeignKey(
        'Group', 
        on_delete=models.CASCADE, 
        related_name='attendances'
    )
    student = models.ForeignKey(
        'Student', 
        on_delete=models.CASCADE, 
        related_name='attendances'
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
        """
        Create attendance records for a specific group for a given month
        
        Args:
            group (Group): The group to create attendance for
            year (int): Year of the month
            month (int): Month to create attendance for
        
        Returns:
            list: List of dates created
        """
        start_date = date(year, month, 1)
        
        # Determine the last day of the month
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        current_date = start_date
        created_dates = []
        
        while current_date <= end_date:
            # Determine if the day should have an attendance record based on group's schedule
            should_create = False
            
            if group.week_days == WeekDayChoices.MON_WED_FRI and current_date.weekday() in [0, 2, 4]:
                should_create = True
            elif group.week_days == WeekDayChoices.TUE_THU_SAT and current_date.weekday() in [1, 3, 5]:
                should_create = True
            
            # Create attendance record if it doesn't already exist
            if should_create:
                students = group.students.all()
                for student in students:
                    cls.objects.get_or_create(
                        group=group, 
                        student=student, 
                        date=current_date,
                        defaults={'status': False}  # Default to absent
                    )
                created_dates.append(current_date)
            
            current_date += timedelta(days=1)
        
        return created_dates

    def save(self, *args, **kwargs):
        """
        Override save method to ensure data integrity
        """
        # Ensure no duplicate attendance records
        existing = Attendance.objects.filter(
            student=self.student, 
            group=self.group, 
            date=self.date
        ).exclude(pk=self.pk)
        
        if existing.exists():
            raise ValueError("An attendance record for this student, group, and date already exists.")
        
        super().save(*args, **kwargs)




class DailyPayment(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='daily_payments')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='daily_payments')
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

        if not self.pk:  # New payment
            if last_payment:
                last_month = last_payment.payment_date.month
                last_year = last_payment.payment_date.year
                
                # If last payment was from a different month, reset remaining amount
                if last_month != current_month or last_year != current_year:
                    self.remaining_amount = self.monthly_fee - self.paid_amount
                else:
                    # Deduct the paid amount from the previous remaining amount
                    self.remaining_amount = last_payment.remaining_amount - self.paid_amount
            else:
                # First payment for the student, set the full monthly fee
                self.remaining_amount = self.monthly_fee - self.paid_amount
        else:
            # In case of update, if the payment is from a new month, reset the balance
            if self.payment_date.month != last_payment.payment_date.month:
                self.remaining_amount = self.monthly_fee - self.paid_amount
            else:
                self.remaining_amount = last_payment.remaining_amount - self.paid_amount

        super().save(*args, **kwargs)

    @classmethod
    def get_student_balance(cls, student_id):
        """O'quvchining joriy balansini qaytaradi"""
        latest_payment = cls.objects.filter(
            student_id=student_id
        ).order_by('-payment_date').first()

        if not latest_payment:
            return 200000  # Or `cls.monthly_fee` if you'd like to refer to it dynamically

        return latest_payment.remaining_amount

    @classmethod
    def get_group_total_remaining(cls, group_id):
        """Guruh bo'yicha umumiy qolgan summani qaytaradi"""
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
                # If no payments found, add the full monthly fee for this student
                student = Student.objects.get(id=payment['student'])
                total_remaining += 200000  # Or `student.monthly_fee` if you want flexibility

        # Handle students who have never made a payment in the group
        students_in_group = Student.objects.filter(group_id=group_id)
        paid_students = [payment['student'] for payment in latest_payments]
        unpaid_students = students_in_group.exclude(id__in=paid_students)

        for student in unpaid_students:
            total_remaining += 200000  # Full balance for unpaid students

        return total_remaining

    @classmethod
    def get_total_payments_across_all_groups(cls):
        """Hamma guruhdagi o‘quvchilarning jami to‘lovlarini hisoblaydi."""
        total_paid = 0

        # Loop over all groups
        for group in Group.objects.all():
            # Loop over all students in the current group
            for student in group.students.all():
                # Sum the paid_amount for each student's DailyPayment records
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
