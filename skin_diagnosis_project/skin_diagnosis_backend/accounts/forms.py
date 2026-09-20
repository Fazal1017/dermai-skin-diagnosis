from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import CustomerProfile, Doctor, Hospital, HospitalStaff


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['phone_number', 'address', 'city', 'state', 'profile_picture']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class RoleBasedLoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}))
    role = forms.ChoiceField(
        choices=[
            ('customer', 'Customer (Patient)'),
            ('doctor', 'Doctor'),
            ('hospital', 'Hospital Staff/Admin')
        ],
        widget=forms.RadioSelect
    )

class RoleBasedSignupForm(UserCreationForm):
    ROLE_CHOICES = [
        ('patient', 'Patient / Customer'),
        ('doctor', 'Doctor'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)

    # Common fields
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15, required=False)

    # Doctor specific fields
    specialization = forms.ChoiceField(choices=[('', 'Select Specialization')] + Doctor.SPECIALIZATION_CHOICES, required=False)
    qualification = forms.CharField(max_length=200, required=False)
    experience_years = forms.IntegerField(min_value=0, required=False)
    consultation_fee = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    hospital_name = forms.CharField(max_length=200, required=False, help_text="Enter hospital name or select from existing")

    # Staff specific fields
    staff_role = forms.ChoiceField(choices=[
        ('', 'Select Role'),
        ('Receptionist', 'Receptionist'),
        ('Admin', 'Administrator'),
        ('Nurse', 'Nurse'),
        ('Lab Tech', 'Laboratory Technician'),
    ], required=False, help_text="e.g., Receptionist, Admin")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')

        if role == 'doctor':
            if not cleaned_data.get('specialization'):
                self.add_error('specialization', 'Specialization required for doctor')
            if not cleaned_data.get('hospital_name'):
                self.add_error('hospital_name', 'Hospital name required')
        if role == 'staff':
            if not cleaned_data.get('hospital_name'):
                self.add_error('hospital_name', 'Hospital name required')
        return cleaned_data

class HospitalRegistrationForm(forms.ModelForm):
    admin_username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Admin Username'}))
    admin_email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Admin Email'}))
    admin_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    admin_confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    class Meta:
        model = Hospital
        fields = ['name', 'registration_number', 'email', 'phone_number',
                  'address', 'city', 'state', 'pincode', 'description', 'established_year']

    def clean_admin_confirm_password(self):
        pwd = self.cleaned_data.get('admin_password')
        confirm = self.cleaned_data.get('admin_confirm_password')
        if pwd != confirm:
            raise forms.ValidationError("Passwords do not match")
        return confirm

    def clean_admin_username(self):
        username = self.cleaned_data.get('admin_username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already taken")
        return username

    def clean_admin_email(self):
        email = self.cleaned_data.get('admin_email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")
        return email
