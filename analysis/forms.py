from django import forms
from resumes.models import Resume
from jobs.models import JobDescription


class RunAnalysisForm(forms.Form):
    resume = forms.ModelChoiceField(
        queryset=Resume.objects.none(),
        empty_label='-- Select a Resume --',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    job_description = forms.ModelChoiceField(
        queryset=JobDescription.objects.none(),
        empty_label='-- Select a Job Description --',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show the current user's own resumes and JDs
        self.fields['resume'].queryset = Resume.objects.filter(
            user=user
        ).order_by('-created_at')
        self.fields['job_description'].queryset = JobDescription.objects.filter(
            user=user
        ).order_by('-created_at')

    def clean(self):
        cleaned_data = super().clean()
        resume = cleaned_data.get('resume')
        jd = cleaned_data.get('job_description')

        if resume and not resume.raw_text.strip():
            raise forms.ValidationError(
                'The selected resume has no text content. '
                'Please upload a valid resume or edit it first.'
            )
        if jd and not jd.raw_text.strip():
            raise forms.ValidationError(
                'The selected job description has no text content. '
                'Please add a valid job description first.'
            )
        return cleaned_data
