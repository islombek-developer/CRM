from users.models import Teacher, Group
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class TeacherPanelView(LoginRequiredMixin, TemplateView):
    template_name = 'teachers/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher  # Ensure this refers to the teacher model linked with the user
        
        # Filter groups related to the logged-in teacher
        groups = Group.objects.filter(teacher=teacher)  # This fetches groups where the teacher is linked

        group_data = []
        for group in groups:
            group_data.append({
                'name': group.name,
                'week_days': group.get_week_days_display(),  # To get the human-readable weekday options
                'monthly_payment': group.monthly_payment,
                'created_at': group.created_at,
                'updated_at': group.updated_at,
            })

        context['groups'] = group_data
        return context