from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from accounts.models import Appointment
from diagnosis.models import PatientDiagnosis
import json
from collections import defaultdict

@login_required
def hospital_analytics(request):
    # Only hospital admins can access
    if not hasattr(request.user, 'hospital_profile'):
        return redirect('customer_dashboard')
    
    # Get all appointments for this hospital (across all doctors)
    appointments = Appointment.objects.filter(
        doctor__hospital=request.user.hospital_profile
    )
    
    # --- Chart 1: Appointments by Status ---
    status_counts = appointments.values('status').annotate(count=Count('id'))
    chart1_labels = [item['status'] for item in status_counts]
    chart1_data = [item['count'] for item in status_counts]
    
    # --- Chart 2: Monthly Appointment Trends ---
    monthly = defaultdict(int)
    for apt in appointments:
        month_key = apt.appointment_date.strftime('%Y-%m')
        monthly[month_key] += 1
    sorted_months = sorted(monthly.keys())
    chart2_labels = sorted_months
    chart2_data = [monthly[m] for m in sorted_months]
    
    # --- Chart 3: Most Common Diseases (from completed appointments) ---
    completed = appointments.filter(status='COMPLETED')
    disease_counts = defaultdict(int)
    for apt in completed:
        if apt.diagnosis:
            disease_counts[apt.diagnosis.disease_name] += 1
    chart3_labels = list(disease_counts.keys())
    chart3_data = list(disease_counts.values())
    
    # --- KPIs ---
    total_appointments = appointments.count()
    completed_count = appointments.filter(status='COMPLETED').count()
    pending_count = appointments.filter(status='PENDING').count()
    conversion_rate = (completed_count / total_appointments * 100) if total_appointments > 0 else 0
    
    # --- Doctor Performance ---
    doctors_performance = []
    for doctor in request.user.hospital_profile.doctors.all():
        doctor_appts = appointments.filter(doctor=doctor)
        completed_by_doctor = doctor_appts.filter(status='COMPLETED').count()
        doctors_performance.append({
            'name': f"Dr. {doctor.name}",
            'total': doctor_appts.count(),
            'completed': completed_by_doctor,
        })
    
    context = {
        'chart1_labels': json.dumps(chart1_labels),
        'chart1_data': json.dumps(chart1_data),
        'chart2_labels': json.dumps(chart2_labels),
        'chart2_data': json.dumps(chart2_data),
        'chart3_labels': json.dumps(chart3_labels),
        'chart3_data': json.dumps(chart3_data),
        'total_appointments': total_appointments,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'conversion_rate': round(conversion_rate, 1),
        'doctors_performance': doctors_performance,
    }
    
    return render(request, 'analytics/hospital_analytics.html', context)
