import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skin_diagnosis_backend.settings')
django.setup()

from accounts.models import CustomerProfile, generate_patient_id

for profile in CustomerProfile.objects.all():
    profile.patient_id = generate_patient_id()
    profile.save()
print("Updated all existing customer profiles with random patient IDs")
