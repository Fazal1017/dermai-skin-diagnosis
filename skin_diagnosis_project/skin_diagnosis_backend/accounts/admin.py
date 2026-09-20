from django.contrib import admin
from .models import CustomerProfile, Hospital, Doctor, Appointment, HospitalStaff

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'city', 'created_at')
    search_fields = ('user__username', 'phone_number', 'city')

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'phone_number', 'is_approved')
    list_filter = ('is_approved', 'city')
    search_fields = ('name', 'registration_number')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'hospital', 'experience_years', 'is_active')
    list_filter = ('specialization', 'is_active', 'hospital')
    search_fields = ('name', 'registration_number')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'doctor', 'appointment_date', 'status')
    list_filter = ('status', 'appointment_date')
    search_fields = ('customer__user__username', 'doctor__name')

@admin.register(HospitalStaff)
class HospitalStaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'hospital', 'role', 'phone_number', 'created_at')
    list_filter = ('hospital', 'role')
    search_fields = ('name', 'user__username')
