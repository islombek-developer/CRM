from .models import Student,User,Teacher,Group,Month,DailyPayment,Attendance,WeekDayChoices
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import render, redirect,get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.views.generic import UpdateView,CreateView,DeleteView,DetailView
from .forms import LoginForm, RegisterForm,GroupForm,UserProfileForm,ResetPasswordForm
from .permissionmixin import AdminRequiredMixin,TeacherRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.contrib import messages
from .models import DailyPayment, Student, Group
from datetime import timezone,datetime, timedelta
from django.urls import reverse_lazy
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.conf.urls import handler404

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)



class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = 'users/group_create.html'
    success_url = reverse_lazy('group_payment')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch teachers with their full names
        context['teachers'] = Teacher.objects.select_related('user').all()
        context['form'] = self.get_form()
        return context

    def form_valid(self, form):
        messages.success(self.request, "Guruh muvaffaqiyatli yaratildi!")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teachers'] = Teacher.objects.select_related('user').all()
        return context

class GroupDeleteView(LoginRequiredMixin, DeleteView):
    model = Group 
    success_url = reverse_lazy('group_payment')  

    def delete(self, request, *args, **kwargs):
        group = self.get_object()
        messages.success(self.request, f"Guruh '{group.name}' muvaffaqiyatli o'chirildi!")
        return super().delete(request, *args, **kwargs)




class GroupPaymentListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'users/group_list.html'
    context_object_name = 'groups'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
class GroupPaymentsListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'users/group.html'
    context_object_name = 'groups'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
            
        return redirect('group_payment_report', group_id=student.group.id)
        
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'users/add_payment.html', {'student': student})

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
    
    return render(request, 'users/payment_history.html', context)

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
    
    return render(request, 'users/group_report.html', context)


class Home(View, LoginRequiredMixin):
    def get(self, request):
        student_count = Student.objects.count()  
        group_count = Group.objects.count()
        total_payments = DailyPayment.get_total_payments_across_all_groups()
        today = datetime.today()
        
        start_of_week = today - timedelta(days=today.weekday())  
        
        end_date_str = start_of_week.strftime('%B %d, %Y')  
        context = {
            'student_count': student_count,
            'group_count': group_count,
            'total_payments': total_payments,
            'date_range': f"{end_date_str}",  
        }
        
        return render(request, 'users/dashboard.html', context)



class LogautView(View):
    def get(self,request):
        logout(request)
        return redirect("/")

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated: 
            if request.user.user_role == 'teacher':
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
                self.logout_other_sessions(user)

                login(request, user)

                if user.user_role == 'teacher':
                    return redirect('teacher/dashboard/')
                elif user.user_role == 'admin':
                    return redirect('/dashboard')

        form = LoginForm()
        return render(request, 'users/login.html', {'form': form})

    def logout_other_sessions(self, user):
        sessions = Session.objects.filter(expire_date__gte=datetime.now())
        for session in sessions:
            data = session.get_decoded()
            if data.get('_auth_user_id') == str(user.id):
                session.delete()


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
                newteacher.save()
            
            return redirect('/dashboard')
        return render(request, 'users/register.html', {'form': form})
    
class TeacherView(LoginRequiredMixin,View):
    def get(self,request):
        teacher=Teacher.objects.all()
        return render(request,'users/teacher.html',{'teacher':teacher})
    

class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/user_profile.html'

    def get_object(self):
        return self.request.user  # Display the logged-in user's profile


# Profile Update View

class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/user_profile_edit.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        # Add any additional logic before saving
        response = super().form_valid(form)
        # Optional: Add a success message
      
        messages.success(self.request, 'Profile updated successfully!')
        return response
    
class ResetPasswordView(LoginRequiredMixin,View):
    def get(self, request):
        form = ResetPasswordForm()
        return render(request, 'users/reset_password.html', {'form':form})

    def post(self, request):
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user = request.user
            user.set_password(new_password)
            user.save()
            return redirect('/')
        form = ResetPasswordForm()
        return render(request, 'users/reset_password.html', {'form':form})
