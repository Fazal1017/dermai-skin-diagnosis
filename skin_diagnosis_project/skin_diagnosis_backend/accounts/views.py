from django.shortcuts import render, redirect, get_object_or_404
import random as _random
import string as _string
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.utils import timezone
from datetime import timedelta
from .forms import RoleBasedSignupForm, UserUpdateForm, ProfileUpdateForm, RoleBasedLoginForm, HospitalRegistrationForm
from .models import Hospital, Doctor, CustomerProfile, Appointment, HospitalStaff
from diagnosis.models import DiagnosisResult, PatientDiagnosis


def register(request):
    if request.method == 'POST':
        form = RoleBasedSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data['role']

            # Get or create hospital if needed
            hospital_name = form.cleaned_data.get('hospital_name')
            hospital = None
            if hospital_name:
                hospital, _ = Hospital.objects.get_or_create(
                    name=hospital_name,
                    defaults={
                        'registration_number': f"TEMP{hospital_name[:5].upper()}",
                        'email': f"contact@{hospital_name.replace(' ', '').lower()}.com",
                        'phone_number': '0000000000',
                        'address': 'Temporary address - update later',
                        'city': 'Unknown',
                        'state': 'Unknown',
                        'pincode': '000000',
                        'is_approved': True
                    }
                )

            if role == 'patient':
                # Signal automatically creates a CustomerProfile, so we update it
                profile, created = CustomerProfile.objects.get_or_create(user=user)
                profile.phone_number = form.cleaned_data.get('phone')
                profile.save()
                messages.success(request, 'Patient account created!')

            elif role == 'doctor':
                # Remove the auto-created CustomerProfile if it exists
                CustomerProfile.objects.filter(user=user).delete()
                
                Doctor.objects.create(
                    user=user,
                    hospital=hospital,
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
                messages.success(request, 'Doctor account created!')

            # Staff accounts are now created only by hospital admins

            return redirect('login')
        else:
            messages.error(request, 'Please correct errors below.')
    else:
        form = RoleBasedSignupForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = RoleBasedLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                # Redirect based on actual profile, not form selection
                if hasattr(user, 'doctor_profile'):
                    return redirect('doctor_dashboard')
                elif hasattr(user, 'staff_profile'):
                    return redirect('staff_dashboard')
                elif hasattr(user, 'customer_profile'):
                    return redirect('customer_dashboard')
                else:
                    return redirect('customer_dashboard')  # fallback
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = RoleBasedLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=getattr(request.user, 'customer_profile', None))
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=getattr(request.user, 'customer_profile', None))

    # Note: DiagnosisResult doesn't have a user field currently,
    # so we fetch the most recent global ones for now to demonstrate the UI.
    recent_diagnoses = DiagnosisResult.objects.all().order_by('-created_at')[:5]

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'recent_diagnoses': recent_diagnoses,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def customer_dashboard(request):
    customer_profile = getattr(request.user, 'customer_profile', None)
    diagnoses = PatientDiagnosis.objects.filter(user=request.user).order_by('-created_at')
    appointments = Appointment.objects.filter(customer=customer_profile).order_by('-appointment_date', '-appointment_time') if customer_profile else []
    appointments_count = appointments.count() if customer_profile else 0
    available_doctors = Doctor.objects.filter(is_active=True)

    context = {
        'customer_profile': customer_profile,
        'diagnoses': diagnoses,
        'appointments': appointments,
        'available_doctors': available_doctors,
        'diagnoses_count': diagnoses.count(),
        'appointments_count': appointments_count,
    }
    return render(request, 'accounts/customer_dashboard.html', context)


@login_required
def doctor_dashboard(request):
    doctor_profile = getattr(request.user, 'doctor_profile', None)
    today = timezone.now().date()

    # Only today's appointments
    appointments = Appointment.objects.filter(
        doctor=doctor_profile,
        appointment_date=today
    ).order_by('appointment_time') if doctor_profile else Appointment.objects.none()

    pending = appointments.filter(status='PENDING')
    confirmed = appointments.filter(status='CONFIRMED')
    completed = appointments.filter(status='COMPLETED')

    context = {
        'doctor_profile': doctor_profile,
        'hospital': doctor_profile.hospital if doctor_profile else None,
        'pending_appointments': pending,
        'confirmed_appointments': confirmed,
        'completed_appointments': completed,
        'today_date': today,
        'total_today': appointments.count(),
    }
    return render(request, 'accounts/doctor_dashboard.html', context)


@login_required
def hospital_dashboard(request):
    hospital_profile = getattr(request.user, 'hospital_profile', None)
    doctors = Doctor.objects.filter(hospital=hospital_profile) if hospital_profile else []
    appointments = Appointment.objects.filter(doctor__hospital=hospital_profile).order_by('-appointment_date', '-appointment_time') if hospital_profile else []
    total_doctors = doctors.count() if hospital_profile else 0
    total_appointments = appointments.count() if hospital_profile else 0
    pending_count = appointments.filter(status='PENDING').count() if hospital_profile else 0
    confirmed_count = appointments.filter(status='CONFIRMED').count() if hospital_profile else 0
    completed_count = appointments.filter(status='COMPLETED').count() if hospital_profile else 0

    context = {
        'hospital_profile': hospital_profile,
        'doctors': doctors,
        'appointments': appointments,
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'completed_count': completed_count,
    }
    return render(request, 'accounts/hospital_dashboard.html', context)


@login_required
def staff_dashboard(request):
    staff_profile = getattr(request.user, 'staff_profile', None)
    hospital = staff_profile.hospital if staff_profile else None
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    day_after = today + timedelta(days=2)

    all_appointments = Appointment.objects.filter(
        doctor__hospital=hospital
    ).order_by('appointment_date', 'appointment_time') if hospital else Appointment.objects.none()

    context = {
        'staff_profile': staff_profile,
        'hospital': hospital,
        'today_appointments': all_appointments.filter(appointment_date=today),
        'tomorrow_appointments': all_appointments.filter(appointment_date=tomorrow),
        'day_after_appointments': all_appointments.filter(appointment_date=day_after),
        'future_appointments': all_appointments.filter(appointment_date__gt=day_after),
        'today': today,
        'tomorrow': tomorrow,
        'day_after': day_after,
    }
    return render(request, 'accounts/staff_dashboard.html', context)


# ─── Appointment Actions ───────────────────────────────────────────────

@login_required
def book_appointment(request, diagnosis_id):
    """Book an appointment based on a diagnosis result."""
    if request.method == 'POST':
        diagnosis = get_object_or_404(PatientDiagnosis, id=diagnosis_id, user=request.user)
        doctor_id = request.POST.get('doctor_id')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason', '')

        doctor = get_object_or_404(Doctor, id=doctor_id, is_active=True)
        customer_profile = request.user.customer_profile

        if Appointment.objects.filter(
            doctor=doctor, appointment_date=appointment_date,
            appointment_time=appointment_time, status__in=['PENDING', 'CONFIRMED']
        ).exists():
            messages.error(request, 'This time slot is already booked. Please choose another.')
            return redirect('customer_dashboard')

        Appointment.objects.create(
            customer=customer_profile, doctor=doctor, diagnosis=diagnosis,
            appointment_date=appointment_date, appointment_time=appointment_time,
            reason=reason, symptoms=diagnosis.disease_name if diagnosis else '',
            status='PENDING'
        )
        
        # Log document sharing
        if diagnosis:
            from diagnosis.models import DiagnosisDocumentHistory
            DiagnosisDocumentHistory.objects.create(
                document=diagnosis,
                action='SHARED',
                performed_by=request.user,
                details=f'Document shared with Dr. {doctor.name} during appointment booking.'
            )
            
        messages.success(request, f'Appointment requested with Dr. {doctor.name}. Waiting for confirmation.')
        return redirect('customer_dashboard')

    return redirect('customer_dashboard')


from .utils import send_appointment_email

@login_required
def confirm_appointment(request, appointment_id):
    """Doctor confirms a pending appointment."""
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor__user=request.user)
    if appointment.status == 'PENDING':
        appointment.status = 'CONFIRMED'
        appointment.confirmed_at = timezone.now()
        appointment.save()
        
        # Send Email Notification
        if appointment.customer.user.email:
            subject = f"Appointment Confirmed with Dr. {appointment.doctor.name}"
            message = f"Hello {appointment.customer.user.get_full_name()},\n\nYour appointment with Dr. {appointment.doctor.name} has been confirmed for {appointment.appointment_date} at {appointment.appointment_time}.\n\nThank you!"
            send_appointment_email(subject, message, appointment.customer.user.email)
            
        messages.success(request, f'Appointment confirmed for {appointment.appointment_date}.')
    else:
        messages.warning(request, 'This appointment cannot be confirmed now.')
    return redirect('doctor_dashboard')


@login_required
def cancel_appointment(request, appointment_id):
    """Cancel appointment (customer or doctor can cancel)."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    user = request.user
    if (hasattr(user, 'customer_profile') and appointment.customer == user.customer_profile) or \
       (hasattr(user, 'doctor_profile') and appointment.doctor == user.doctor_profile):
        appointment.status = 'CANCELLED'
        appointment.save()
        messages.info(request, 'Appointment has been cancelled.')
    else:
        messages.error(request, 'You are not authorized to cancel this appointment.')

    if hasattr(user, 'doctor_profile'):
        return redirect('doctor_dashboard')
    else:
        return redirect('customer_dashboard')


@login_required
def complete_appointment(request, appointment_id):
    """Doctor marks an appointment as completed."""
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor__user=request.user)
    if appointment.status == 'CONFIRMED':
        appointment.status = 'COMPLETED'
        appointment.save()
        messages.success(request, f'Appointment with {appointment.customer.user.username} marked as completed.')
    else:
        messages.warning(request, 'Only confirmed appointments can be marked as completed.')
    return redirect('doctor_dashboard')


@login_required
def book_by_doctor(request, doctor_id):
    """Direct booking from a doctor card."""
    if request.method == 'POST':
        doctor = get_object_or_404(Doctor, id=doctor_id, is_active=True)
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason', '')
        customer_profile = request.user.customer_profile

        if Appointment.objects.filter(
            doctor=doctor, appointment_date=appointment_date,
            appointment_time=appointment_time, status__in=['PENDING', 'CONFIRMED']
        ).exists():
            messages.error(request, 'Slot already booked.')
            return redirect('customer_dashboard')

        Appointment.objects.create(
            customer=customer_profile, doctor=doctor,
            appointment_date=appointment_date, appointment_time=appointment_time,
            reason=reason, status='PENDING'
        )
        messages.success(request, f'Appointment requested with Dr. {doctor.name}.')
        return redirect('customer_dashboard')

    doctor = get_object_or_404(Doctor, id=doctor_id)
    return render(request, 'accounts/book_appointment.html', {'doctor': doctor})

# --- Reschedule Features ---
@login_required
def request_reschedule(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, customer=request.user.customer_profile)
    if request.method == 'POST':
        date = request.POST.get('reschedule_date')
        time = request.POST.get('reschedule_time')
        if date and time:
            appointment.reschedule_requested_date = date
            appointment.reschedule_requested_time = time
            appointment.reschedule_status = 'pending'
            appointment.save()
            messages.success(request, 'Reschedule request sent to the doctor.')
    return redirect('customer_dashboard')

@login_required
def approve_reschedule(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor_profile)
    if appointment.reschedule_status == 'pending':
        appointment.appointment_date = appointment.reschedule_requested_date
        appointment.appointment_time = appointment.reschedule_requested_time
        appointment.reschedule_status = 'approved'
        appointment.save()
        messages.success(request, 'Reschedule approved.')
    return redirect('doctor_dashboard')

@login_required
def reject_reschedule(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor_profile)
    if appointment.reschedule_status == 'pending':
        appointment.reschedule_status = 'rejected'
        appointment.save()
        messages.info(request, 'Reschedule rejected.')
    return redirect('doctor_dashboard')

# --- Prescription Features ---
from .models import Prescription

@login_required
def write_prescription(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user.doctor_profile)
    if request.method == 'POST':
        medicines = request.POST.get('medicines')
        dosage = request.POST.get('dosage')
        notes = request.POST.get('notes', '')
        pdf_file = request.FILES.get('pdf_file')
        
        Prescription.objects.update_or_create(
            appointment=appointment,
            defaults={
                'doctor': appointment.doctor,
                'patient': appointment.customer,
                'medicines': medicines,
                'dosage': dosage,
                'notes': notes,
                'pdf_file': pdf_file
            }
        )
        messages.success(request, 'Prescription saved.')
        return redirect('doctor_dashboard')
    
    prescription = getattr(appointment, 'prescription', None)
    return render(request, 'accounts/write_prescription.html', {'appointment': appointment, 'prescription': prescription})

@login_required
def view_prescription(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    # Check authorization
    if not (hasattr(request.user, 'customer_profile') and appointment.customer == request.user.customer_profile) and \
       not (hasattr(request.user, 'doctor_profile') and appointment.doctor == request.user.doctor_profile):
        messages.error(request, 'Unauthorized.')
        return redirect('customer_dashboard')
        
    prescription = get_object_or_404(Prescription, appointment=appointment)
    return render(request, 'accounts/view_prescription.html', {'prescription': prescription})

# --- Feature 6: Find Nearby Hospitals ---
def find_hospitals(request):
    city = request.GET.get('city', '')
    hospitals = Hospital.objects.filter(is_approved=True)
    if city:
        hospitals = hospitals.filter(city__icontains=city)
    return render(request, 'accounts/find_hospitals.html', {'hospitals': hospitals, 'city': city})

# --- Feature 8: Export Patient History as PDF ---
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse

@login_required
def export_diagnoses_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="diagnoses.pdf"'
    p = canvas.Canvas(response, pagesize=letter)
    
    diagnoses = PatientDiagnosis.objects.filter(user=request.user)
    y = 750
    p.drawString(100, y, "Your Diagnosis History")
    y -= 30
    for diag in diagnoses:
        p.drawString(100, y, f"{diag.created_at.date()} - {diag.disease_name} ({diag.confidence}%)")
        y -= 20
    p.showPage()
    p.save()
    return response

# --- Feature 9: Submit Review ---
from .models import Review
@login_required
def submit_review(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, customer=request.user.customer_profile)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        Review.objects.update_or_create(
            appointment=appointment,
            defaults={'rating': rating, 'comment': comment}
        )
        messages.success(request, 'Review submitted successfully!')
    return redirect('customer_dashboard')

# --- Hospital Registration ---
def register_hospital(request):
    if request.method == 'POST':
        form = HospitalRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            hospital = form.save(commit=False)
            hospital.is_approved = True
            hospital.save()
            
            # Generate random password for admin
            raw_password = _generate_random_password()
            
            admin_user = User.objects.create_user(
                username=form.cleaned_data['admin_username'],
                email=form.cleaned_data['admin_email'],
                password=raw_password
            )
            admin_user.first_name = form.cleaned_data.get('name', '').split()[0] if form.cleaned_data.get('name') else ''
            admin_user.save()
            
            hospital.admin_user = admin_user
            hospital.user = admin_user
            hospital.save()
            
            messages.success(request, f"Hospital registered! Your Hospital ID: {hospital.hospital_id}")
            messages.info(request, f"Admin Username: {admin_user.username} | Temporary Password: {raw_password} (Please change after login)")
            
            login(request, admin_user)
            return redirect('hospital_admin_dashboard')
    else:
        form = HospitalRegistrationForm()
    return render(request, 'accounts/register_hospital.html', {'form': form})

# --- Hospital Admin Dashboard ---
def _generate_random_password(length=10):
    chars = _string.ascii_letters + _string.digits
    return ''.join(_random.choice(chars) for _ in range(length))

@login_required
def hospital_admin_dashboard(request):
    try:
        hospital = request.user.admin_hospital
    except:
        messages.error(request, 'You are not authorized as hospital admin.')
        return redirect('login')
    
    if request.method == 'POST' and 'add_staff' in request.POST:
        name = request.POST.get('staff_name')
        email = request.POST.get('staff_email')
        role = request.POST.get('staff_role', 'Receptionist')
        raw_password = _generate_random_password()
        username = email
        user = User.objects.create_user(username=username, email=email, password=raw_password)
        user.first_name = name.split()[0] if name else ''
        user.last_name = ' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
        user.save()
        HospitalStaff.objects.create(user=user, hospital=hospital, name=name, phone_number='', email=email, role=role)
        messages.success(request, f'Staff {name} created. Username: {username}, Password: {raw_password}')
        return redirect('hospital_admin_dashboard')
    
    staff_members = HospitalStaff.objects.filter(hospital=hospital)
    return render(request, 'accounts/hospital_admin_dashboard.html', {'hospital': hospital, 'staff_members': staff_members})

