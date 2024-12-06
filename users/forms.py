from django import forms
from .models import Student,User,Teacher,Group,DailyPayment,Attendance,WeekDayChoices

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','image', 'phone_number', 'address', 'jobs']
        widgets = {
            'phone_number': forms.TextInput(),
            'address': forms.TextInput(),
            'jobs': forms.TextInput(),
        }

class GroupForm(forms.ModelForm):
    name = forms.CharField(
        label='Guruh nomi', 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    teacher = forms.ModelChoiceField(
        label="O'qituvchi", 
        queryset=Teacher.objects.select_related('user').all(), 
        empty_label="O'qituvchini tanlang",
        widget=forms.Select(attrs={'class': 'form-control'}),
        to_field_name='id'
    )
    
    week_days = forms.ChoiceField(
        label='Kunlari', 
        choices=WeekDayChoices.choices,
        initial=WeekDayChoices.MON_WED_FRI,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    monthly_payment = forms.IntegerField(
        label='Oylik tolov', 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Group
        fields = ['name', 'teacher', 'week_days', 'monthly_payment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the label for each teacher to show full name
        self.fields['teacher'].label_from_instance = lambda obj: obj.get_full_name()

class StudentForm(forms.ModelForm):
    group_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'phone','phone2']

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
        fields = ['first_name', 'last_name', 'phone', 'phone2', 'group']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),  # Corrected to TextInput
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),   # Corrected to TextInput
            'phone': forms.TextInput(attrs={'class': 'form-control'}),       # Corrected to TextInput
            'phone2': forms.TextInput(attrs={'class': 'form-control'}),      # Corrected to TextInput
            'group': forms.Select(attrs={'class': 'form-control', 'id': 'edit-group'}),  # Keep as Select if group is a ForeignKey
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

class ResetPasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput({"class": "form-control", "placeholder": "Old Password"}))
    new_password = forms.CharField(widget=forms.PasswordInput({"class": "form-control", "placeholder": "New Password"}))
    confirrm_password = forms.CharField(widget=forms.PasswordInput({"class": "form-control", "placeholder": "Confirm Password"}))

    def clean_confirm_password(self):
        new_password = self.cleaned_data['new_password']
        new_password = self.cleaned_data['confirm_password']

        if new_password !=confirm__password:
            raise forms.ValidationError("passwords dont mach")
        
        return confirm_password