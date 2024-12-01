from django.shortcuts import render, redirect,get_object_or_404
from django.views.generic.edit import CreateView,DeleteView,UpdateView
from django.urls import reverse_lazy
from .models import Student,Group
from .forms import StudentForm ,StudentFormUpdate
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .views import View

class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'users/student.html'

    def get_initial(self):
        initial = super().get_initial()
        group_id = self.kwargs.get('group_id')  
        try:
            group = Group.objects.get(id=group_id)
            initial['group'] = group  
        except Group.DoesNotExist:
            pass
        return initial

    def form_valid(self, form):
        student = form.save(commit=True)
        group_id = self.kwargs.get('group_id')

        if not group_id:
            messages.error(self.request, "Guruh ID'si taqdim etilmadi!")
            return redirect(self.request.path_info)

        try:
            group = Group.objects.get(id=group_id)
            student.group = group
        except Group.DoesNotExist:
            messages.error(self.request, "Bunday guruh mavjud emas!")
            return redirect(self.request.path_info)

        student.save()
        messages.success(self.request, f"{student.first_name} {student.last_name} muvaffaqiyatli qo'shildi!")
        return redirect('student_list', group_id=group.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group_id = self.kwargs.get('group_id')  
        context['group_id'] = group_id  
        return context

# class StudentCreateView(LoginRequiredMixin, View):
#     def get(self, request, group_id=None):
#         form = StudentForm(initial={'group_id': group_id} if group_id else None)
#         return render(request, 'users/student.html', {'form': form})

#     def post(self, request, group_id=None):
#         # POST ma'lumotlariga group_id qo'shish
#         post_data = request.POST.copy() 
#         post_data['group_id'] = group_id or post_data.get('group_id')
        
#         form = StudentForm(post_data)
#         if form.is_valid():
#             student = form.save()
#             messages.success(request, "Student muvaffaqiyatli qo'shildi")
#             return redirect('student_list', group_id=group_id) 
#         return render(request, 'users/student.html', {'form': form})

class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'users/student.html'
    context_object_name = 'students'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = get_object_or_404(Group, id=self.kwargs.get('group_id'))
        return context

    def get_queryset(self):
        group_id = self.kwargs.get('group_id')
        if group_id:
            return Student.objects.filter(group_id=group_id)
        return Student.objects.all()


class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentFormUpdate
    template_name = 'users/student.html'
    success_url = reverse_lazy('group_payment')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.all()  
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
