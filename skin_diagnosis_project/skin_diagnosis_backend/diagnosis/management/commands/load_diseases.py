from django.core.management.base import BaseCommand
from diagnosis.models import Disease

class Command(BaseCommand):
    help = 'Load skin disease data'

    def handle(self, *args, **options):
        diseases_data = [
            {
                'name': 'Acne',
                'prescription': 'Topical benzoyl peroxide (2.5%-10%) once daily. If no improvement in 4-6 weeks, add topical retinoid (adapalene). For moderate-severe cases, oral antibiotics (doxycycline) with topical combination therapy.',
                'doctor_specialty': 'Dermatologist (or General Practitioner for mild cases)',
                'referral_needed': False,
                'urgency_level': 'Low',
                'precautions': 'Wash face twice daily\nAvoid oily food\nDo not pop pimples\nUse non-comedogenic products'
            },
            {
                'name': 'Eczema',
                'prescription': 'Emollients (moisturizers) applied multiple times daily. Topical corticosteroids (hydrocortisone 1% for mild, stronger for moderate). Antihistamines for itching.',
                'doctor_specialty': 'Dermatologist (Allergist/Immunologist for severe cases)',
                'referral_needed': True,
                'urgency_level': 'Medium',
                'precautions': 'Moisturize regularly\nAvoid harsh soaps\nWear cotton clothes\nAvoid known triggers'
            },
            {
                'name': 'Melanoma',
                'prescription': 'URGENT: Immediate surgical excision with wide margins. Follow-up with oncology for staging. May require immunotherapy (pembrolizumab), targeted therapy (BRAF inhibitors if mutation positive), or chemotherapy.',
                'doctor_specialty': 'Dermatologist (for biopsy) → Surgical Oncologist → Medical Oncologist',
                'referral_needed': True,
                'urgency_level': 'High',
                'precautions': 'Avoid sun exposure\nUse SPF 50+ sunscreen\nRegular skin self-exams\nDo not delay seeking care'
            },
            {
                'name': 'Psoriasis',
                'prescription': 'Topical corticosteroids (for mild). Vitamin D analogues (calcipotriene). UV phototherapy for moderate. Systemic biologics (adalimumab, secukinumab) for severe.',
                'doctor_specialty': 'Dermatologist (Rheumatologist if joint pain present)',
                'referral_needed': True,
                'urgency_level': 'Medium',
                'precautions': 'Avoid stress\nUse mild soaps\nKeep skin hydrated\nAvoid alcohol and smoking'
            },
            {
                'name': 'Urticaria (Hives)',
                'prescription': 'Second-generation antihistamines (cetirizine 10mg, loratadine 10mg, or fexofenadine 180mg) once daily. For severe cases, add H2 blocker (famotidine) or short course oral corticosteroids.',
                'doctor_specialty': 'General Practitioner (Allergist/Immunologist for chronic >6 weeks)',
                'referral_needed': False,
                'urgency_level': 'Low',
                'precautions': 'Avoid known allergens\nWear loose clothing\nApply cold compress\nAvoid NSAIDs if trigger unknown'
            }
        ]
        
        for data in diseases_data:
            obj, created = Disease.objects.get_or_create(name=data['name'], defaults=data)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Added {obj.name}'))
            else:
                self.stdout.write(f'{obj.name} already exists')
