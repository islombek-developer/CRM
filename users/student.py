from django.shortcuts import render, redirect,get_object_or_404
from django.views.generic.edit import CreateView,DeleteView,UpdateView
from django.urls import reverse_lazy
from .models import Student,Group
from .forms import StudentForm  
from django.views.generic import ListView

class CreateStudentView(CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'users/student_form.html'
    success_url = reverse_lazy('student-list')  

    
class StudentListView(ListView):
    model = Student
    template_name = 'users/student.html'
    context_object_name = 'students'

    def get_queryset(self):
        group_id = self.kwargs.get('group_id')
        group = get_object_or_404(Group, id=group_id)
        return Student.objects.filter(group=group)

class UpdateStudentView(UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'users/student_form.html'
    success_url = reverse_lazy('student-list')

class DeleteStudentView(DeleteView):
    model = Student
    template_name = 'users/student_confirm_delete.html'
    success_url = reverse_lazy('student-list')