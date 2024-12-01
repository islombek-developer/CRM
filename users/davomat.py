from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Group, Attendance, Student
from django.utils import timezone
from django.contrib import messages
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.db.models import F, ExpressionWrapper, FloatField, Count,Q



@login_required
def attendance_list(request, group_id):
    """
    Comprehensive attendance tracking view for a specific group
    Kunlarni va ishtirok etish statistikasini ko'rsatish
    """
    # Gruppani olib kelish (404 xatoligini tekshirish)
    group = get_object_or_404(Group, id=group_id)

    # Filtrlar uchun parametrlarni olish
    year = request.GET.get('year')
    month = request.GET.get('month')
    day = request.GET.get('day')  # New filter for day
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Attendance queryset'ini yaratish
    attendances = Attendance.objects.filter(group=group)

    # Yil bo'yicha filtrash
    if year:
        try:
            year = int(year)
            attendances = attendances.filter(date__year=year)
        except ValueError:
            pass

    # Oy bo'yicha filtrash
    if month:
        try:
            month = int(month)
            attendances = attendances.filter(date__month=month)
        except ValueError:
            pass

    # Kun bo'yicha filtrash
    if day:
        try:
            day = int(day)
            attendances = attendances.filter(date__day=day)
        except ValueError:
            pass

    # Sana oralig'i bo'yicha filtrash
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            attendances = attendances.filter(date__range=[start_date, end_date])
        except ValueError:
            pass

    # Kunlar bo'yicha guruhlash
    grouped_attendances = {}
    for attendance in attendances.order_by('-date'):
        grouped_attendances.setdefault(attendance.date, []).append(attendance)

    # Attendance statistikasini hisoblash
    total_attendance_stats = attendances.aggregate(
        total_count=Count('id'),
        present_count=Count('id', filter=Q(status=True)),
        absent_count=Count('id', filter=Q(status=False)),
        present_percentage=ExpressionWrapper(
            Count('id', filter=Q(status=True)) * 100.0 / Count('id'), 
            output_field=FloatField()
        )
    )

    # Filtrlar uchun mavjud yillar, oylar va kunlarni aniqlash
    available_years = sorted(set(attendances.values_list('date__year', flat=True)))
    available_months = sorted(set(attendances.values_list('date__month', flat=True)))
    available_days = sorted(set(attendances.values_list('date__day', flat=True)))  # Days of attendance

    context = {
        'group': group,
        'grouped_attendances': dict(sorted(grouped_attendances.items(), reverse=True)),
        'attendance_stats': total_attendance_stats,
        'available_years': available_years,
        'available_months': available_months,
        'available_days': available_days,  # Pass available days to template
        'selected_year': year,
        'selected_month': month,
        'selected_day': day,  # Pass the selected day to template
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'users/attendance_list.html', context)

@login_required
def attendance_page(request, group_id):
    """
    Render the attendance page for a specific group
    """
    try:
        # Get the specific group
        group = Group.objects.get(id=group_id)
        
        # Get all students in the group
        students = group.students.all()
        
        # Get today's date
        today = timezone.localdate()
        
        # Prepare attendance data
        attendance_data = []
        for student in students:
            # Check if attendance exists for this student and today
            attendance, created = Attendance.objects.get_or_create(
                group=group,
                student=student,
                date=today,
                defaults={'status': False}
            )
            
            attendance_data.append({
                'student': student,
                'attendance': attendance
            })
        
        context = {
            'group': group,
            'attendance_data': attendance_data,
            'today': today
        }
        
        return render(request, 'users/attendance.html', context)
    
    except Group.DoesNotExist:
        # Handle case where group doesn't exist
        return redirect('group_list')  # Adjust this to your actual route

@login_required
def save_attendance(request, group_id):
    """
    Save attendance for a group
    """
    if request.method == 'POST':
        # Get the group
        group = Group.objects.get(id=group_id)
        
        # Get today's date
        today = timezone.localdate()
        
        # Process each student's attendance
        for key, value in request.POST.items():
            if key.startswith('attendance_'):
                student_id = key.split('_')[1]
                try:
                    student = Student.objects.get(id=student_id)
                    
                    # Find or create attendance record
                    attendance, created = Attendance.objects.get_or_create(
                        group=group,
                        student=student,
                        date=today,
                        defaults={'status': value == 'present'}
                    )
                    
                    # Update if not created
                    if not created:
                        attendance.status = (value == 'present')
                        attendance.save()
                
                except (Student.DoesNotExist, ValueError):
                    # Log error or handle appropriately
                    continue
        
        # Redirect back to attendance page or show success message
        return redirect('attendance_list', group_id=group_id)
    
    # If not a POST request, redirect
    return redirect('attendance_group')  # Adjust to your actual route

class GroupAttendListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'users/attendanc.html'
    context_object_name = 'groups'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context