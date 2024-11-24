from django.views.generic import TemplateView
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin

class TeacherPanelView(LoginRequiredMixin, TemplateView):
    template_name = 'teacher_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher  # Joriy o‘qituvchi

        # O'qituvchining guruhlari
        groups = teacher.groups.all()

        # Guruhlar ma'lumotlarini yig‘ish
        group_data = []
        for group in groups:
            group_data.append({
                'name': group.name,
                'student_count': group.student_count,
                'total_payment_status': group.total_payment_status,
            })

        context['groups'] = group_data
        return context