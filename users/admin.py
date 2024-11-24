from django.contrib import admin
from .models import Student,User,Teacher,Group,Day,Month,DailyPayment,Attendance
admin.site.register(Student)
admin.site.register(User)
admin.site.register(Teacher)
admin.site.register(Group)
admin.site.register(Day)
admin.site.register(Month)
admin.site.register(DailyPayment)
admin.site.register(Attendance)
