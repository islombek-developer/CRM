from django import forms
from .models import Student,User,Teacher,Group,DailyPayment,Attendance,WeekDayChoices

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'teacher', 'week_days', 'monthly_payment']  

        def __init__(self, *args, **kwargs):
            teachers = kwargs.pop('teachers', None)
            super().__init__(*args, **kwargs)
            if teachers:
                self.fields['teachers'].queryset = teachers

class StudentForm(forms.ModelForm):
    group_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'phone']

    def save(self, commit=True):
        instance = super().save(commit=False)
        group_id = self.cleaned_data.get('group_id')
        if group_id:
            try:
                instance.group = Group.objects.get(id=group_id)
            except Group.DoesNotExist:
                raise forms.ValidationError("Guruh topilmadi")
        
        if commit:
            instance.save()
        return instance


class StudentFormUpdate(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'phone', 'group']
        widgets = {
            'group': forms.Select(attrs={'class': 'form-control', 'id': 'edit-group'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            phone = ''.join(filter(str.isdigit, phone))
            if not phone.startswith('+998'):
                raise forms.ValidationError("Telefon raqami noto'g'ri formatda")
        return phone

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput({"class": "form-control", "placeholder": "Username"}))
    password = forms.CharField(widget=forms.PasswordInput({"class": "form-control", "placeholder": "Password"}))

class RegisterForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput({"class": "form-control", "placeholder": "Name"}))
    phone_number = forms.CharField(widget=forms.TextInput({"class": "form-control", "placeholder": "Phone Number"}))
    first_name = forms.CharField(widget=forms.TextInput({"class": "form-control", "placeholder": "First Name"}))
    last_name = forms.CharField(widget=forms.TextInput({"class": "form-control", "placeholder": "Last Name"}))
    password = forms.CharField(widget=forms.PasswordInput({"class": "form-control", "placeholder": "Password"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput({"class": "form-control", "placeholder": "Confirm Password"}))

    class Meta:
        model = User
        fields = ('__all__')

    def clean_confirm_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']

        if password != confirm_password:    
            raise forms.ValidationError("Passwords do not match")
        return password

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput({"class": "form-control", "placeholder": "Username"}))
    password = forms.CharField(widget=forms.PasswordInput({"class": "form-control", "placeholder": "Password"}))

class RegisterForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput({"class": "form-control", "placeholder": "Name"}))
    phone_number = forms.CharField(widget=forms.TextInput({"class": "form-control", "placeholder": "Phone Number"}))
    first_name = forms.CharField(widget=forms.TextInput({"class": "form-control", "placeholder": "First Name"}))
    last_name = forms.CharField(widget=forms.TextInput({"class": "form-control", "placeholder": "Last Name"}))
    password = forms.CharField(widget=forms.PasswordInput({"class": "form-control", "placeholder": "Password"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput({"class": "form-control", "placeholder": "Confirm Password"}))

    class Meta:
        model = User
        fields = ('username', 'phone_number', 'first_name', 'last_name', 'password', 'confirm_password', 'user_role')

    def clean_confirm_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']

        if password != confirm_password:    
            raise forms.ValidationError("Passwords do not match")
        return password

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            if self.cleaned_data['user_role'] == 'teacher':
                teacher = Teacher.objects.create(user=user)
                teacher.save()
        return user
