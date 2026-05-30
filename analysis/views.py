from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AnalysisResult
from .forms import RunAnalysisForm
from resumes.models import Resume
from jobs.models import JobDescription
from services.skill_extractor import extract_skills, extract_keywords
from services.scorer import run_full_scoring
from services.recommender import generate_suggestions
from services.optimizer import optimize_resume


@login_required
def run_analysis_view(request):
    # Pre-select resume or JD if passed via GET params
    initial = {}
    if request.GET.get('resume'):
        initial['resume'] = request.GET.get('resume')
    if request.GET.get('jd'):
        initial['job_description'] = request.GET.get('jd')

    if request.method == 'POST':
        form = RunAnalysisForm(request.user, request.POST)
        if form.is_valid():
            resume = form.cleaned_data['resume']
            jd     = form.cleaned_data['job_description']

            # Make sure JD has parsed skills — reparse if empty
            if not jd.parsed_skills:
                jd.parsed_skills   = extract_skills(jd.raw_text)
                jd.parsed_keywords = extract_keywords(jd.raw_text, top_n=30)
                jd.save(update_fields=['parsed_skills', 'parsed_keywords'])

            # Extract skills from resume
            resume_skills = extract_skills(resume.raw_text)

            # Run scoring engine
            scores = run_full_scoring(
                resume_text            = resume.raw_text,
                resume_skills          = resume_skills,
                jd_text                = jd.raw_text,
                jd_skills              = jd.parsed_skills,
                jd_keywords            = jd.parsed_keywords,
                jd_experience_required = jd.experience_required,
                jd_education_required  = jd.education_required,
            )

            # Generate suggestions
            suggestions = generate_suggestions(
                missing_skills   = scores['missing_skills'],
                missing_keywords = scores['missing_keywords'],
                skill_score      = scores['skill_match_score'],
                keyword_score    = scores['keyword_match_score'],
                experience_score = scores['experience_score'],
                education_score  = scores['education_score'],
                final_score      = scores['final_score'],
                jd_title         = jd.title,
            )

            # Save result
            result = AnalysisResult.objects.create(
                user             = request.user,
                resume           = resume,
                job_description  = jd,
                skill_match_score   = scores['skill_match_score'],
                keyword_match_score = scores['keyword_match_score'],
                experience_score    = scores['experience_score'],
                education_score     = scores['education_score'],
                final_score         = scores['final_score'],
                matched_skills      = scores['matched_skills'],
                missing_skills      = scores['missing_skills'],
                matched_keywords    = scores['matched_keywords'],
                missing_keywords    = scores['missing_keywords'],
                suggestions         = suggestions,
            )

            messages.success(
                request,
                f'Analysis complete! Final score: {result.final_score:.1f}% — {result.get_label()}'
            )
            return redirect('analysis:result', pk=result.pk)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = RunAnalysisForm(request.user, initial=initial)

    return render(request, 'analysis/run.html', {'form': form})


@login_required
def analysis_result_view(request, pk):
    result = get_object_or_404(AnalysisResult, pk=pk, user=request.user)

    # Handle optimize request
    if request.method == 'POST' and request.POST.get('action') == 'optimize':
        optimized_text = optimize_resume(
            resume_text    = result.resume.raw_text,
            missing_skills = result.missing_skills,
            jd_title       = result.job_description.title,
            matched_skills = result.matched_skills,
        )
        # Save as new optimised version
        new_resume = Resume(
            user         = request.user,
            title        = result.resume.title + ' (Optimised)',
            raw_text     = optimized_text,
            version      = result.resume.version + 1,
            is_optimized = True,
            parent       = result.resume if result.resume.parent is None else result.resume.parent,
        )
        new_resume.save()
        messages.success(
            request,
            f'Optimised resume saved as version {new_resume.version}. '
            f'You can now edit it further in the Resume Editor.'
        )
        return redirect('resumes:editor', pk=new_resume.pk)

    context = {
        'result': result,
        'score_class': result.get_score_class(),
        'label': result.get_label(),
        'label_color': result.get_label_color(),
    }
    return render(request, 'analysis/result.html', context)


@login_required
def analysis_history_view(request):
    results = AnalysisResult.objects.filter(user=request.user).select_related(
        'resume', 'job_description'
    )
    return render(request, 'analysis/history.html', {'results': results})


@login_required
def delete_analysis_view(request, pk):
    result = get_object_or_404(AnalysisResult, pk=pk, user=request.user)
    if request.method == 'POST':
        result.delete()
        messages.success(request, 'Analysis deleted.')
    return redirect('analysis:history')
