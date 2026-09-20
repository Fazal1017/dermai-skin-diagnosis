from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('register/hospital/', views.register_hospital, name='register_hospital'),
    path('hospital/admin/dashboard/', views.hospital_admin_dashboard, name='hospital_admin_dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Role-specific dashboards
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('dashboard/hospital/', views.hospital_dashboard, name='hospital_dashboard'),
    path('dashboard/staff/', views.staff_dashboard, name='staff_dashboard'),
    
    # Appointment endpoints
    path('appointment/book/<int:diagnosis_id>/', views.book_appointment, name='book_appointment'),
    path('appointment/book/doctor/<int:doctor_id>/', views.book_by_doctor, name='book_by_doctor'),
    path('appointment/confirm/<int:appointment_id>/', views.confirm_appointment, name='confirm_appointment'),
    path('appointment/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('appointment/complete/<int:appointment_id>/', views.complete_appointment, name='complete_appointment'),
    
    # Reschedule endpoints
    path('appointment/reschedule/request/<int:appointment_id>/', views.request_reschedule, name='request_reschedule'),
    path('appointment/reschedule/approve/<int:appointment_id>/', views.approve_reschedule, name='approve_reschedule'),
    path('appointment/reschedule/reject/<int:appointment_id>/', views.reject_reschedule, name='reject_reschedule'),
    
    # Prescription endpoints
    path('prescription/write/<int:appointment_id>/', views.write_prescription, name='write_prescription'),
    path('prescription/view/<int:appointment_id>/', views.view_prescription, name='view_prescription'),
    
    # Feature 6: Find Hospitals
    path('find-hospitals/', views.find_hospitals, name='find_hospitals'),
    
    # Feature 8: Export PDF
    path('export-pdf/', views.export_diagnoses_pdf, name='export_diagnoses_pdf'),
    
    # Feature 9: Review
    path('review/submit/<int:appointment_id>/', views.submit_review, name='submit_review'),
]
