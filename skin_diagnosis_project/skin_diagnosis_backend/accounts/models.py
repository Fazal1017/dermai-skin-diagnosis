from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import os

import uuid

def generate_patient_id():
    import secrets
    return f"PT-{secrets.token_hex(4).upper()}"

class CustomerProfile(models.Model):
    """
    Profile for normal users/patients.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    patient_id = models.CharField(max_length=20, unique=True, default=generate_patient_id, editable=False)
    
    # Basic Information
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        blank=True,
        null=True
    )
    
    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    
    # Medical History (optional)
    medical_history = models.TextField(blank=True, help_text="Past conditions, allergies, etc.")
    
    # Profile Picture
    profile_picture = models.ImageField(
        upload_to='profile_pics/customers/',
        default='profile_pics/default.jpg',
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Customer: {self.user.username}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.profile_picture:
            try:
                pic_path = self.profile_picture.path
                if os.path.isfile(pic_path):
                    img = Image.open(pic_path)
                    width, height = img.size
                    if width > 300 or height > 300:
                        img.thumbnail((300, 300))
                        img.save(pic_path)
            except (ValueError, FileNotFoundError):
                pass

import random
import string

class Hospital(models.Model):
    """
    Hospital/Clinic entity that will own the doctors and appointments.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hospital_profile', null=True, blank=True)
    name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=50, unique=True, help_text="Hospital registration ID/Certificate number")
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    
    # Description
    description = models.TextField(blank=True)
    established_year = models.IntegerField(blank=True, null=True)
    
    # Hospital Logo
    logo = models.ImageField(upload_to='hospital_logos/', blank=True, null=True)
    
    # Admin user for the hospital
    admin_user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='admin_hospital', null=True, blank=True)
    
    # Random unique Hospital ID
    hospital_id = models.CharField(max_length=10, unique=True, blank=True)
    
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.hospital_id:
            while True:
                new_id = 'HOS' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                if not Hospital.objects.filter(hospital_id=new_id).exists():
                    self.hospital_id = new_id
                    break
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.hospital_id})"

class Doctor(models.Model):
    """
    Doctor profile, linked to a Hospital and User (for login access).
    """
    SPECIALIZATION_CHOICES = [
        ('DER', 'Dermatologist'),
        ('GEN', 'General Physician'),
        ('ONC', 'Oncologist'),
        ('ALL', 'Allergist/Immunologist'),
        ('PED', 'Pediatric Dermatologist'),
        ('COS', 'Cosmetic Dermatologist'),
        ('SUR', 'Dermatologic Surgeon'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='doctors')
    
    # Professional Information
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=3, choices=SPECIALIZATION_CHOICES)
    qualification = models.CharField(max_length=200, help_text="e.g., MBBS, MD Dermatology")
    experience_years = models.IntegerField(default=0)
    registration_number = models.CharField(max_length=50, help_text="Medical Council Registration")
    
    # Contact
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    
    # Consultation Details
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    available_days = models.CharField(max_length=100, blank=True, help_text="e.g., Monday, Wednesday, Friday")
    available_time_start = models.TimeField(blank=True, null=True)
    available_time_end = models.TimeField(blank=True, null=True)
    
    # Bio/Description
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='doctor_pics/', blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Dr. {self.name} - {self.get_specialization_display()}"

class Appointment(models.Model):
    """
    Appointment booking between a Customer/Patient and a Doctor.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('RESCHEDULED', 'Rescheduled'),
    ]
    
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    diagnosis = models.ForeignKey('diagnosis.PatientDiagnosis', on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    
    # Appointment Details
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField(blank=True, help_text="Reason for consultation")
    symptoms = models.TextField(blank=True)
    
    # Status Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, help_text="Doctor's notes after consultation")
    
    # Timestamps
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    
    # Reschedule functionality
    reschedule_requested_date = models.DateField(null=True, blank=True)
    reschedule_requested_time = models.TimeField(null=True, blank=True)
    reschedule_status = models.CharField(max_length=20, choices=[('none','None'),('pending','Pending'),('approved','Approved'),('rejected','Rejected')], default='none')
    
    def __str__(self):
        return f"Appointment: {self.customer.user.username} with Dr. {self.doctor.name} on {self.appointment_date}"

class HospitalStaff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='staff_members')
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    role = models.CharField(max_length=50, default="Receptionist")  # e.g., Receptionist, Admin
    profile_picture = models.ImageField(upload_to='staff_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.hospital.name}"

class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='prescription')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    medicines = models.TextField()
    dosage = models.TextField()
    notes = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to='prescriptions/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Prescription for {self.patient.user.username} by Dr. {self.doctor.name}"

class Review(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review for Dr. {self.appointment.doctor.name} - {self.rating} Stars"
