from django import forms

class ImageUploadForm(forms.Form):
    """Form for uploading skin lesion images for diagnosis"""
    image = forms.ImageField(
        label='Upload a skin image',
        help_text='Supported formats: JPG, PNG, GIF (max 5MB)'
    )
    
    def clean_image(self):
        """Validate uploaded image"""
        image = self.cleaned_data.get('image')
        
        if image:
            # Check file size (5MB max)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file is too large. Max size: 5MB")
            
            # Check file extension
            allowed_formats = ['image/jpeg', 'image/png', 'image/gif']
            if image.content_type not in allowed_formats:
                raise forms.ValidationError(
                    "Invalid image format. Supported: JPG, PNG, GIF"
                )
        
        return image


class DiagnosisNotesForm(forms.Form):
    """Form for adding clinical notes to diagnosis"""
    patient_id = forms.CharField(
        max_length=50,
        required=False,
        label='Patient ID',
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., P12345',
            'class': 'form-control'
        })
    )
    notes = forms.CharField(
        max_length=500,
        required=False,
        label='Clinical Notes',
        widget=forms.Textarea(attrs={
            'placeholder': 'e.g., Lesion on left arm, itchy...',
            'class': 'form-control',
            'rows': 4
        })
    )
