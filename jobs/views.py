from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import JobDescription
from .forms import JobDescriptionForm
from services.extractor import extract_text, clean_text
from services.skill_extractor import extract_skills, extract_keywords
from services.parser import parse_jd
from services.naming import generate_jd_name, sanitize_name


@login_required
def upload_jd_view(request):
    if request.method == 'POST':
        form = JobDescriptionForm(request.POST, request.FILES)
        if form.is_valid():
            jd = form.save(commit=False)
            jd.user = request.user

            # Extract text from file if no text pasted
            if not jd.raw_text and jd.file:
                extracted = extract_text(request.FILES.get('file'))
                jd.raw_text = clean_text(extracted)

            if not jd.raw_text.strip():
                messages.error(
                    request,
                    'Could not extract text from the uploaded file. '
                    'Please paste the text manually.'
                )
                return render(request, 'jobs/upload.html', {'form': form})

            # Auto-generate title if blank
            role_hint = form.cleaned_data.get('role_hint', '')
            if not jd.title or not jd.title.strip():
                jd.title = generate_jd_name(
                    user=request.user,
                    raw_text=jd.raw_text,
                    role_hint=role_hint,
                )

            # Run NLP parsing
            parsed = parse_jd(jd.raw_text)
            jd.experience_required = jd.experience_required or parsed['experience_required']
            jd.education_required  = jd.education_required  or parsed['education_required']

            # Extract skills and keywords
            jd.parsed_skills   = extract_skills(jd.raw_text)
            jd.parsed_keywords = extract_keywords(jd.raw_text, top_n=30)

            jd.save()
            messages.success(
                request,
                f'Job description "{jd.title}" saved. '
                f'{len(jd.parsed_skills)} skills extracted.'
            )
            return redirect('jobs:detail', pk=jd.pk)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = JobDescriptionForm()

    return render(request, 'jobs/upload.html', {'form': form})


@login_required
def jd_detail_view(request, pk):
    jd = get_object_or_404(JobDescription, pk=pk, user=request.user)
    return render(request, 'jobs/detail.html', {'jd': jd})


@login_required
def delete_jd_view(request, pk):
    jd = get_object_or_404(JobDescription, pk=pk, user=request.user)
    if request.method == 'POST':
        title = jd.title
        jd.delete()
        messages.success(request, f'Job description "{title}" deleted.')
    return redirect('dashboard:index')


@login_required
def list_jd_view(request):
    jds = JobDescription.objects.filter(user=request.user)
    return render(request, 'jobs/list.html', {'jds': jds})
