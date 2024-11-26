from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum
from django.core.validators import MaxValueValidator,FileExtensionValidator
from datetime import datetime, date,timedelta
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
            total += payment - (200000/30)  # To‘lov yetishmasa minus bo‘ladi
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
        total_days = Day.objects.filter(group=self.group).count()
        if total_days == 0:
            return 0
        present_days = Attendance.objects.filter(
            student=self, 
            status=True
        ).count()
        return (present_days / total_days) * 100
    
    @property
    def remaining_payment(self):
        latest_payment = DailyPayment.objects.filter(
            student=self
        ).order_by('-payment_date').first()
        
        return latest_payment.remaining_amount if latest_payment else 200000

    @property
    def student_count(self):
        """Guruhdagi o‘quvchilar sonini hisoblaydi."""
        return self.students.count()


    @property
    def total_payment_status(self):
        """Guruhdagi o‘quvchilarning umumiy oylik to‘lovlarini hisoblaydi."""
        total = 0
        for student in self.students.all():
            # Talabaning jami oylik to‘lovini olamiz
            payment = student.monthlypayments.aggregate(total=Sum('oylik'))['total'] or 0
            total += payment - (200000/30)  # To‘lov yetishmasa minus bo‘ladi
        return total



    @property
    def total_remaining(self):
        return DailyPayment.get_group_total_remaining(self.id)

class Day(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='days')
    date = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['group', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.date.strftime('%B %d, %Y')} - {self.group.name}"

    @property
    def month(self):
        return self.date.strftime('%B')

    @property
    def day_of_month(self):
        return self.date.day

    @property
    def attendance_count(self):
        return self.attendance_set.filter(status=True).count()
    
    @classmethod
    def create_days_for_month(cls, group, year, month):
        """Berilgan oy uchun darskunlarini yaratish"""
        start_date = date(year, month, 1)
        
        # Oyning oxirgi kuni
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        current_date = start_date
        created_days = []
        
        while current_date <= end_date:
            # Guruhning dars kunlarini tekshirish
            should_create = False
            
          
            if group.week_days == WeekDayChoices.MON_WED_FRI and current_date.weekday() in [0, 2, 4]:
                should_create = True
            elif group.week_days == WeekDayChoices.TUE_THU_SAT and current_date.weekday() in [1, 3, 5]:
                should_create = True
                
            if should_create:
                day, created = cls.objects.get_or_create(
                    group=group,
                    date=current_date
                )
                if created:
                    created_days.append(day)
                    
            current_date += timedelta(days=1)
            
        return created_days

class Attendance(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='attendance')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.ForeignKey(Day, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date__date']
    
    def __str__(self):
        status_text = "Keldi" if self.status else "Kelmadi"
        return f"{self.student.full_name} - {self.date.date} - {status_text}"

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
        if not self.pk:  # Yangi to'lov uchun
            last_payment = DailyPayment.objects.filter(
                student=self.student
            ).order_by('-payment_date').first()
            
            if last_payment:
                self.remaining_amount = last_payment.remaining_amount - self.paid_amount
            else:
                self.remaining_amount = self.monthly_fee - self.paid_amount
        
        super().save(*args, **kwargs)
    
    @classmethod
    def get_student_balance(cls, student_id):
        """O'quvchining joriy balansini qaytaradi"""
        latest_payment = cls.objects.filter(
            student_id=student_id
        ).order_by('-payment_date').first()
        
        return latest_payment.remaining_amount if latest_payment else 200000
    
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
                
        return total_remaining
    
    @property
    def total_payment_status(self):
        """Guruhdagi o‘quvchilarning umumiy oylik to‘lovlarini hisoblaydi."""
        total = 0
        for student in self.students.all():
            # Talabaning jami oylik to‘lovini olamiz
            payment = student.monthlypayments.aggregate(total=Sum('oylik'))['total'] or 0
            total += payment - (200000/30)  # To‘lov yetishmasa minus bo‘ladi
        return total
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
# Signals
@receiver(post_save, sender=Group)
def create_initial_days(sender, instance, created, **kwargs):
    """Yangi guruh yaratilganda joriy oy uchun dars kunlarini yaratish"""
    if created:
        today = date.today()
        Day.create_days_for_month(instance, today.year, today.month)

class Month(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='month')
    month = models.CharField(max_length=150)

    def __str__(self) -> str:
        return f"{self.month} "



# class DailyPayment(models.Model):
#     group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='daily_payments')
#     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='daily_payments')
#     payment_date = models.DateField(auto_now_add=True)
#     monthly_fee = models.IntegerField(default=200000)  # Oylik to'lov
#     remaining_amount = models.IntegerField()  # Qolgan summa
#     paid_amount = models.IntegerField()  # Shu kun to'langan summa
    
#     def save(self, *args, **kwargs):
#         # Agar yangi yozuv bo'lsa
#         if not self.pk:
#             # Oxirgi to'lov yozuvini tekshirish
#             last_payment = DailyPayment.objects.filter(
#                 student=self.student
#             ).order_by('-payment_date').first()
            
#             if last_payment:
#                 # Agar oldingi to'lov mavjud bo'lsa, qolgan summani olish
#                 self.remaining_amount = last_payment.remaining_amount - self.paid_amount
#             else:
#                 # Agar birinchi to'lov bo'lsa
#                 self.remaining_amount = self.monthly_fee - self.paid_amount
        
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.student.first_name} - {self.payment_date} - Qoldi: {self.remaining_amount}"
    
#     @classmethod
#     def get_student_balance(cls, student_id):
#         """O'quvchining joriy balansini qaytaradi"""
#         latest_payment = cls.objects.filter(
#             student_id=student_id
#         ).order_by('-payment_date').first()
        
#         return latest_payment.remaining_amount if latest_payment else 200000
    
#     @classmethod
#     def get_group_total_remaining(cls, group_id):
#         """Guruh bo'yicha umumiy qolgan summani qaytaradi"""
#         latest_payments = cls.objects.filter(
#             group_id=group_id
#         ).values('student').annotate(
#             latest_date=models.Max('payment_date')
#         )
        
#         total_remaining = 0
#         for payment in latest_payments:
#             student_latest = cls.objects.filter(
#                 student_id=payment['student'],
#                 payment_date=payment['latest_date']
#             ).first()
#             if student_latest:
#                 total_remaining += student_latest.remaining_amount
                
#         return total_remaining



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
