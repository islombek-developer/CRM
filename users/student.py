from django.shortcuts import render, redirect,get_object_or_404
from django.views.generic.edit import CreateView,DeleteView,UpdateView
from django.urls import reverse_lazy
from .models import Student,Group
from .forms import StudentForm ,StudentFormUpdate
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'users/student.html'
    success_url = reverse_lazy('student_list')

    def form_valid(self, form):
        try:
            print("Form data:", self.request.POST)
            student = form.save(commit=False)
            
            group = Group.objects.first()  
            print("Selected group:", group)
            
            student.group = group
            
            student.save()
            print("Student saved successfully:", student)
            
            messages.success(self.request, "Student muvaffaqiyatli qo'shildi!")
            return super().form_valid(form)
        except Exception as e:
            print("Error saving student:", str(e))
            messages.error(self.request, f"Xatolik yuz berdi: {str(e)}")
            return redirect('student_list', group_id=group.id if group else 0)

    def form_invalid(self, form):
        print("Form errors:", form.errors)
        messages.error(self.request, "Formada xatolik bor. Iltimos, qayta urinib ko'ring.")
        return redirect('group_payment')
    
class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'users/student.html'
    context_object_name = 'students'

 
    def get_queryset(self):
        group_id = self.kwargs.get('group_id')
        group = get_object_or_404(Group, id=group_id)
        return Student.objects.filter(group=group)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = StudentForm()  
        return context
    

class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentFormUpdate
    template_name = 'users/student.html'
    success_url = reverse_lazy('group_payment')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.all()  # Add all groups to the context
        return context

    def form_valid(self, form):
        messages.success(self.request, "Student ma'lumotlari yangilandi!")
        return super().form_valid(form)

class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    success_url = reverse_lazy('group_payment')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Student o'chirildi!")
        return super().delete(request, *args, **kwargs)
class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    template_name = 'users/delete_student.html'  
    success_url = reverse_lazy('group_payment')  

    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        messages.success(self.request, f"Guruh '{student.first_name}' muvaffaqiyatli o'chirildi!")
        return super().delete(request, *args, **kwargs)
