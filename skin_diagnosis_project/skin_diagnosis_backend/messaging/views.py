from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Message
from accounts.models import Appointment

@login_required
def appointment_chat(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    # Authorise: only the customer or the assigned doctor can view.
    if not (hasattr(appointment.customer, 'user') and appointment.customer.user == request.user or hasattr(appointment.doctor, 'user') and appointment.doctor.user == request.user):
        messages.error(request, 'You are not authorised to view this chat.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                appointment=appointment,
                sender=request.user,
                content=content
            )
        return redirect('appointment_chat', appointment_id=appointment_id)
    
    messages_list = appointment.messages.all().order_by('created_at')
    # Mark as read (optional)
    unread = messages_list.filter(is_read=False).exclude(sender=request.user)
    unread.update(is_read=True)
    
    other_party_name = appointment.doctor.name if hasattr(appointment.customer, 'user') and appointment.customer.user == request.user else appointment.customer.user.get_full_name()
    
    return render(request, 'messaging/chat.html', {
        'appointment': appointment,
        'messages': messages_list,
        'other_party_name': other_party_name
    })
