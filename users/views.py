from .models import Student,User,Teacher,Group,Day,Month,DailyPayment,Attendance
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import render, redirect,get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.views.generic import UpdateView
from .forms import LoginForm, RegisterForm
from .permissionmixin import AdminRequiredMixin,TeacherRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.contrib import messages
from .models import DailyPayment, Student, Group
from datetime import timezone


class GroupPaymentListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'payments/group_list.html'
    context_object_name = 'groups'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for group in context['groups']:
            group.total_remaining = DailyPayment.get_group_total_remaining(group.id)
        return context

class StudentPaymentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'payments/student_list.html'
    context_object_name = 'students'

    def get_queryset(self):
        self.group = get_object_or_404(Group, id=self.kwargs['group_id'])
        return Student.objects.filter(group=self.group)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.group
        
        # Har bir student uchun oxirgi to'lov va qolgan summani olish
        for student in context['students']:
            latest_payment = DailyPayment.objects.filter(
                student=student
            ).order_by('-payment_date').first()
            
            student.remaining_amount = latest_payment.remaining_amount if latest_payment else 200000
            student.last_payment_date = latest_payment.payment_date if latest_payment else None
            
        return context

@login_required
def add_payment(request, student_id):
    if request.method == 'POST':
        paid_amount = request.POST.get('paid_amount')
        try:
            student = Student.objects.get(id=student_id)
            payment = DailyPayment(
                group=student.group,
                student=student,
                paid_amount=int(paid_amount)
            )
            payment.save()
            messages.success(request, "To'lov muvaffaqiyatli qo'shildi!")
            
        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
            
        return redirect('student_payment_list', group_id=student.group.id)
        
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'payments/add_payment.html', {'student': student})

@login_required
def student_payment_history(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    payments = DailyPayment.objects.filter(
        student=student
    ).order_by('-payment_date')
    
    # Umumiy statistika
    total_paid = payments.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
    remaining_amount = DailyPayment.get_student_balance(student_id)
    
    context = {
        'student': student,
        'payments': payments,
        'total_paid': total_paid,
        'remaining_amount': remaining_amount
    }
    
    return render(request, 'payments/payment_history.html', context)

@login_required
def group_payment_report(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    current_month = timezone.now().month
    
    # Guruh bo'yicha oylik statistika
    monthly_stats = DailyPayment.objects.filter(
        group=group,
        payment_date__month=current_month
    ).aggregate(
        total_paid=Sum('paid_amount'),
        total_remaining=Sum('remaining_amount')
    )
    
    # Har bir student uchun oylik to'lovlar
    students = Student.objects.filter(group=group)
    student_payments = []
    
    for student in students:
        payments = DailyPayment.objects.filter(
            student=student,
            payment_date__month=current_month
        )
        total_paid = payments.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
        remaining = DailyPayment.get_student_balance(student.id)
        
        student_payments.append({
            'student': student,
            'total_paid': total_paid,
            'remaining': remaining
        })
    
    context = {
        'group': group,
        'monthly_stats': monthly_stats,
        'student_payments': student_payments
    }
    
    return render(request, 'payments/group_report.html', context)

def home(request):
    return render(request, 'index.html')



class LoginView(View,LoginRequiredMixin):
    def get(self, request):
        if request.user.is_authenticated: 
            if request.user.user_role == 'student':
                return redirect('students/dashboard')
            elif request.user.user_role == 'teacher':
                return redirect('teachers/dashboard')
            elif request.user.user_role == 'admin':
                return redirect('/dashboard')

        form = LoginForm()
        return render(request, 'users/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                if user.user_role == 'teacher':
                    return redirect('teachers/dashboard')
                elif user.user_role == 'admin':
                    return redirect('/dashboard')


        form = LoginForm()
        return render(request, 'users/login.html', {'form': form})


class RegisterView(AdminRequiredMixin, View):
    
    def get(self, request):
        form = RegisterForm()
        return render(request, 'users/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            

                
            if user.user_role == 'teacher':
                newteacher = Teacher.objects.create(user=user)
                
                if form.cleaned_data['team']:
                    team = form.cleaned_data['team']
                    team.teacher = newteacher
                    team.save()
            
            return redirect('/dashboard')
        return render(request, 'users/register.html', {'form': form})