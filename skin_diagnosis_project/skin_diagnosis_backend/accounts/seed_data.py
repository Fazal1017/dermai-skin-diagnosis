"""
Seed script: Creates a Hospital, a Doctor user, and links them.
Run with: python manage.py shell < accounts/seed_data.py
"""
from accounts.models import Hospital, Doctor
from django.contrib.auth.models import User

# Create a hospital
hospital, created = Hospital.objects.get_or_create(
    registration_number="HOSP123",
    defaults={
        'name': "City Dermatology Clinic",
        'email': "contact@cityderm.com",
        'phone_number': "9876543210",
        'address': "123 Main Street",
        'city': "Bangalore",
        'state': "Karnataka",
        'pincode': "560001",
        'is_approved': True,
    }
)
if created:
    print("Hospital 'City Dermatology Clinic' created.")
else:
    print("Hospital already exists.")

# Create a doctor user
doctor_user, created = User.objects.get_or_create(
    username="drsharma",
    defaults={
        'first_name': "Rajesh",
        'last_name': "Sharma",
    }
)
if created:
    doctor_user.set_password("doctor123")
    doctor_user.save()
    print("Doctor user 'drsharma' created (password: doctor123)")
else:
    print("Doctor user already exists.")

# Create doctor profile
doctor, created = Doctor.objects.get_or_create(
    user=doctor_user,
    defaults={
        'hospital': hospital,
        'name': "Rajesh Sharma",
        'specialization': "DER",
        'qualification': "MBBS, MD Dermatology",
        'experience_years': 12,
        'registration_number': "MC12345",
        'phone_number': "9988776655",
        'email': "drsharma@cityderm.com",
        'consultation_fee': 800.00,
        'available_days': "Monday, Wednesday, Friday",
        'is_active': True,
    }
)
if created:
    print("Doctor profile created for Dr. Rajesh Sharma.")
else:
    print("Doctor profile already exists.")

print("\nSample data created successfully!")
print("Doctor login -> username: drsharma, password: doctor123")
