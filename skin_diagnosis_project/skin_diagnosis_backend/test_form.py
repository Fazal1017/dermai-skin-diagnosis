import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skin_diagnosis_backend.settings')
django.setup()

from accounts.forms import RoleBasedSignupForm
from accounts.models import Doctor

data = {
    'role': 'doctor',
    'first_name': 'Test',
    'last_name': 'Doc',
    'username': 'testdoc2',
    'email': 'testdoc2@example.com',
    'phone': '1234567890',
    'password1': 'StrongPass123',
    'password2': 'StrongPass123',
    'hospital_name': 'Apollo',
    'specialization': 'Dermatologist',
    'qualification': 'MBBS',
    'experience_years': '5',
    'consultation_fee': '500',
}

form = RoleBasedSignupForm(data=data)
if not form.is_valid():
    print("Form is invalid:")
    print(form.errors)
else:
    print("Form is valid")
    try:
        user = form.save()
        role = form.cleaned_data['role']
        Doctor.objects.create(
            user=user,
            hospital=None,
            name=f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}",
            specialization=form.cleaned_data['specialization'],
            qualification=form.cleaned_data.get('qualification', ''),
            experience_years=form.cleaned_data.get('experience_years') or 0,
            registration_number=f"REG{user.id}",
            phone_number=form.cleaned_data.get('phone', ''),
            email=form.cleaned_data['email'],
            consultation_fee=form.cleaned_data.get('consultation_fee') or 0,
            is_active=True
        )
        print("Doctor created successfully!")
    except Exception as e:
        print("Error creating doctor:", e)
