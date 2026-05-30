from django import forms
from .models import Resume


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


class ResumeUploadForm(forms.ModelForm):
    role_hint = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=False,
        label='Role (for auto-naming & optimization)',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_role_hint',
        }),
    )

    class Meta:
        model = Resume
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Software Engineer Resume 2024',
                'id': 'id_resume_title',
                'autocomplete': 'off',
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.docx',
                'id': 'id_resume_file',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = False
        self.fields['title'].label = 'Resume Title (optional)'
        self.fields['title'].help_text = 'Leave blank to auto-generate — e.g. pythonresume01'

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            raise forms.ValidationError('Please upload a resume file.')
        if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise forms.ValidationError(f'File size must be under {MAX_FILE_SIZE_MB}MB.')
        name = file.name.lower()
        if not (name.endswith('.pdf') or name.endswith('.docx')):
            raise forms.ValidationError('Only PDF and DOCX files are supported.')
        return file

    def clean_title(self):
        title = self.cleaned_data.get('title', '')
        if title and len(title.strip()) < 2:
            raise forms.ValidationError(
                'Title must be at least 2 characters, or leave blank to auto-generate.'
            )
        from services.naming import sanitize_name
        return sanitize_name(title)


class ResumeEditForm(forms.ModelForm):
    role_hint = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=False,
        label='Role (for export & optimization)',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_role_hint',
        }),
    )

    class Meta:
        model = Resume
        fields = ['title', 'raw_text']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Resume title',
                'id': 'id_resume_title',
            }),
            'raw_text': forms.Textarea(attrs={
                'class': 'form-control resume-editor-textarea',
                'rows': 25,
                'placeholder': 'Edit your resume content here...',
            }),
        }

    def clean_raw_text(self):
        text = self.cleaned_data.get('raw_text', '')
        if len(text.strip()) < 100:
            raise forms.ValidationError(
                'Resume content is too short. Please provide at least 100 characters.'
            )
        return text
