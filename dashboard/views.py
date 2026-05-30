from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from analysis.models import AnalysisResult
from resumes.models import Resume
from jobs.models import JobDescription


@login_required
def dashboard_index_view(request):
    analyses     = AnalysisResult.objects.filter(user=request.user).select_related(
                       'resume', 'job_description')[:10]
    resumes      = Resume.objects.filter(user=request.user)[:5]
    jds          = JobDescription.objects.filter(user=request.user)[:5]
    resume_count = Resume.objects.filter(user=request.user).count()
    jd_count     = JobDescription.objects.filter(user=request.user).count()
    analysis_count = AnalysisResult.objects.filter(user=request.user).count()

    top_score = None
    avg_score = None
    if analyses:
        scores    = [a.final_score for a in analyses]
        top_score = max(scores)
        avg_score = round(sum(scores) / len(scores), 1)

    context = {
        'analyses':       analyses,
        'resumes':        resumes,
        'jds':            jds,
        'resume_count':   resume_count,
        'jd_count':       jd_count,
        'analysis_count': analysis_count,
        'top_score':      top_score,
        'avg_score':      avg_score,
    }
    return render(request, 'dashboard/index.html', context)
