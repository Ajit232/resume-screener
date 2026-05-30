import re
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Resume
from .forms import ResumeUploadForm, ResumeEditForm
from services.extractor import extract_text, clean_text
from services.naming import generate_resume_name, sanitize_name
from services.latex_generator import generate_latex


@login_required
def upload_resume_view(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user

            uploaded_file = request.FILES.get('file')
            if uploaded_file:
                extracted = extract_text(uploaded_file)
                resume.raw_text = clean_text(extracted)

            if not resume.raw_text.strip():
                messages.error(
                    request,
                    'Could not extract text from the file. '
                    'Please use the editor to add content manually.'
                )

            # Auto-generate title if blank
            role_hint = form.cleaned_data.get('role_hint', '')
            if not resume.title or not resume.title.strip():
                resume.title = generate_resume_name(
                    user=request.user,
                    raw_text=resume.raw_text,
                    role_hint=role_hint,
                )

            resume.save()
            messages.success(
                request,
                f'Resume "{resume.title}" uploaded. '
                f'{resume.word_count()} words extracted.'
            )
            return redirect('resumes:detail', pk=resume.pk)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = ResumeUploadForm()

    return render(request, 'resumes/upload.html', {'form': form})


@login_required
def resume_detail_view(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    versions = resume.get_all_versions() if resume.parent is None else []
    return render(request, 'resumes/detail.html', {
        'resume': resume,
        'versions': versions,
    })


@login_required
def resume_editor_view(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ResumeEditForm(request.POST, instance=resume)
        if form.is_valid():
            new_resume = Resume(
                user=request.user,
                title=form.cleaned_data['title'] or resume.title,
                raw_text=form.cleaned_data['raw_text'],
                version=resume.version + 1,
                parent=resume if resume.parent is None else resume.parent,
                is_optimized=False,
            )
            new_resume.save()
            messages.success(
                request,
                f'Resume saved as version {new_resume.version}.'
            )
            return redirect('resumes:detail', pk=new_resume.pk)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = ResumeEditForm(instance=resume)

    return render(request, 'resumes/editor.html', {
        'form': form,
        'resume': resume,
    })


@login_required
def delete_resume_view(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    if request.method == 'POST':
        title = resume.title
        resume.delete()
        messages.success(request, f'Resume "{title}" deleted.')
    return redirect('dashboard:index')


@login_required
def list_resumes_view(request):
    resumes = Resume.objects.filter(user=request.user)
    return render(request, 'resumes/list.html', {'resumes': resumes})


# ---------------------------------------------------------------------------
# Export views
# ---------------------------------------------------------------------------

@login_required
def export_ats_view(request, pk):
    """
    Serve a clean ATS-optimised HTML print page.
    Opens in a new tab — user uses browser print / Save as PDF.
    No Bootstrap, no navbar. Pure structured HTML for ATS scanners.
    """
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    return render(request, 'resumes/ats_export.html', {
        'resume': resume,
        'sections': _parse_sections(resume.raw_text),
    })


@login_required
def export_latex_view(request, pk):
    """
    Generate and serve a .tex file download.
    """
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    latex_content = generate_latex(resume.raw_text, resume_title=resume.title)
    safe_name = _safe_filename(resume.title) or 'resume'
    response = HttpResponse(latex_content, content_type='application/x-tex')
    response['Content-Disposition'] = f'attachment; filename="{safe_name}.tex"'
    return response


@login_required
def export_styled_view(request, pk):
    """
    Render the styled PDF print page — full visual layout.
    Opens in a new tab; browser print dialog used to save as PDF.
    """
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    return render(request, 'resumes/styled_export.html', {
        'resume': resume,
        'sections': _parse_sections(resume.raw_text),
    })


# ---------------------------------------------------------------------------
# Helper: parse raw_text into ordered sections
# ---------------------------------------------------------------------------

SECTION_HEADING_RE = re.compile(
    r'^\s*(PROFESSIONAL SUMMARY|SUMMARY|PROFILE|OBJECTIVE|'
    r'WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|EXPERIENCE|EMPLOYMENT|'
    r'EDUCATION|ACADEMIC BACKGROUND|'
    r'TECHNICAL SKILLS|CORE COMPETENCIES|SKILLS|'
    r'PROJECTS|KEY PROJECTS|'
    r'CERTIFICATIONS?|CERTIFICATES?|'
    r'AWARDS?|ACHIEVEMENTS?|HONORS?|'
    r'LANGUAGES?|INTERESTS?|VOLUNTEERING?)\s*$',
    re.IGNORECASE,
)


def _parse_sections(raw_text):
    """
    Split raw_text into ordered list of (heading, lines) tuples.
    First section heading='header' contains name + contact lines.
    """
    if not raw_text:
        return [('header', [])]

    lines = raw_text.split('\n')
    sections = []
    current_heading = 'header'
    current_lines = []

    for line in lines:
        if SECTION_HEADING_RE.match(line):
            sections.append((current_heading, current_lines))
            current_heading = line.strip().title()
            current_lines = []
        else:
            current_lines.append(line)

    sections.append((current_heading, current_lines))
    return sections


def _safe_filename(title):
    """Convert a resume title to a safe ASCII filename slug."""
    if not title:
        return 'resume'
    slug = re.sub(r'[^\w\s\-]', '', title.lower())
    slug = re.sub(r'[\s\-]+', '_', slug).strip('_')
    return slug[:60] or 'resume'
