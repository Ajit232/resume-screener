from django import forms
from .models import JobDescription


MAX_FILE_SIZE_MB = 10

ROLE_CHOICES = [
    ('', 'Auto-detect from content'),
    ('python',      'Python Developer'),
    ('java',        'Java Developer'),
    ('javascript',  'JavaScript / Frontend Developer'),
    ('fullstack',   'Full Stack Developer'),
    ('datascience', 'Data Scientist'),
    ('dataanalyst', 'Data Analyst'),
    ('devops',      'DevOps Engineer'),
    ('cloud',       'Cloud Engineer'),
    ('backend',     'Backend Developer'),
    ('frontend',    'Frontend Developer'),
    ('mobile',      'Mobile Developer'),
    ('general',     'General Software Engineer'),
]


class JobDescriptionForm(forms.ModelForm):
    # Optional role hint for auto-naming
    role_hint = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=False,
        label='Role (for auto-naming)',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_role_hint'}),
    )

    class Meta:
        model = JobDescription
        fields = ['title', 'company', 'raw_text', 'file',
                  'experience_required', 'education_required']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Senior Python Developer',
                'id': 'id_jd_title',
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Google (optional)'
            }),
            'raw_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 12,
                'placeholder': 'Paste the full job description here...',
                'id': 'id_jd_raw_text',
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.docx'
            }),
            'experience_required': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 3-5 years (optional)'
            }),
            'education_required': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make title optional — auto-generated if blank
        self.fields['title'].required = False
        self.fields['title'].label = 'Job Title (optional)'
        self.fields['title'].help_text = 'Leave blank to auto-generate a name'

    def clean(self):
        cleaned_data = super().clean()
        raw_text = cleaned_data.get('raw_text')
        file     = cleaned_data.get('file')

        if not raw_text and not file:
            raise forms.ValidationError(
                'Please either paste the job description text or upload a file.'
            )
        return cleaned_data

    def clean_raw_text(self):
        text = self.cleaned_data.get('raw_text', '')
        if text and len(text.strip()) < 50:
            raise forms.ValidationError(
                'Job description is too short. Please provide at least 50 characters.'
            )
        return text

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise forms.ValidationError(f'File size must be under {MAX_FILE_SIZE_MB}MB.')
            name = file.name.lower()
            if not (name.endswith('.pdf') or name.endswith('.docx')):
                raise forms.ValidationError('Only PDF and DOCX files are supported.')
        return file

    def clean_title(self):
        # Title is optional — blank is fine, auto-name applied in the view
        title = self.cleaned_data.get('title', '')
        if title and len(title.strip()) < 2:
            raise forms.ValidationError('Job title must be at least 2 characters, or leave blank to auto-generate.')
        from services.naming import sanitize_name
        return sanitize_name(title)
