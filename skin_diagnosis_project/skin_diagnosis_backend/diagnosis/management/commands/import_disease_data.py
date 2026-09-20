from django.core.management.base import BaseCommand
from diagnosis.models import Disease

class Command(BaseCommand):
    help = 'Imports disease data'

    def handle(self, *args, **options):
        diseases_data = [
            {
                'name': 'Acne',
                'description': 'A skin condition that occurs when your hair follicles become plugged with oil and dead skin cells.',
                'first_line_treatment': 'Topical benzoyl peroxide or topical retinoids. Oral antibiotics for moderate cases. Severe acne may need oral isotretinoin.',
                'doctor_specialty': 'Dermatologist (or General Practitioner for mild cases)',
                'referral_needed': True, # "Referral needed for severe cases only"
                'urgency_level': 'Medium'
            },
            {
                'name': 'Eczema',
                'description': 'A condition that makes your skin red and itchy. It\'s common in children but can occur at any age.',
                'first_line_treatment': 'Emollients (moisturizers) and mild-potency topical corticosteroids.',
                'doctor_specialty': 'Dermatologist, Allergist for severe cases',
                'referral_needed': True,
                'urgency_level': 'Medium'
            },
            {
                'name': 'Melanoma',
                'description': 'The most serious type of skin cancer, develops in the cells (melanocytes) that produce melanin.',
                'first_line_treatment': '🔴 Urgent surgical removal. Multimodality therapy including surgery, immunotherapy, and targeted therapy.',
                'doctor_specialty': 'Dermatologist (for biopsy), Surgical Oncologist, Medical Oncologist',
                'referral_needed': True,
                'urgency_level': 'High'
            },
            {
                'name': 'Psoriasis',
                'description': 'A skin disease that causes red, itchy scaly patches, most commonly on the knees, elbows, trunk and scalp.',
                'first_line_treatment': 'Topical treatments (emollients, corticosteroids) for mild cases. Systemic treatments (biologics) for moderate to severe cases.',
                'doctor_specialty': 'Dermatologist, Rheumatologist if arthritis present',
                'referral_needed': True,
                'urgency_level': 'Medium'
            },
            {
                'name': 'Urticaria (Hives)',
                'description': 'A skin rash triggered by a reaction to food, medicine, or other irritants.',
                'first_line_treatment': 'Second-generation antihistamines (e.g., cetirizine, loratadine). Taken daily for prevention.',
                'doctor_specialty': 'General Practitioner, Allergist/Immunologist for chronic cases',
                'referral_needed': True,
                'urgency_level': 'Low'
            }
        ]
        
        for data in diseases_data:
            obj, created = Disease.objects.update_or_create(
                name=data['name'], 
                defaults=data
            )
            action = 'created' if created else 'updated'
            self.stdout.write(self.style.SUCCESS(f'Successfully {action} {obj.name}'))
