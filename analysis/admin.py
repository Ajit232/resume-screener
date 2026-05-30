from django.contrib import admin
from django.utils.html import format_html
from .models import AnalysisResult


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'resume_title', 'jd_title',
        'score_display', 'skill_match_score',
        'keyword_match_score', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = [
        'user__username',
        'resume__title',
        'job_description__title'
    ]
    readonly_fields = [
        'final_score', 'skill_match_score', 'keyword_match_score',
        'experience_score', 'education_score', 'matched_skills',
        'missing_skills', 'matched_keywords', 'missing_keywords',
        'suggestions', 'created_at'
    ]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Linked Records', {
            'fields': ('user', 'resume', 'job_description')
        }),
        ('Scores', {
            'fields': (
                'final_score', 'skill_match_score',
                'keyword_match_score', 'experience_score', 'education_score',
            )
        }),
        ('Matched Skills & Keywords', {
            'fields': ('matched_skills', 'matched_keywords'),
            'classes': ('collapse',)
        }),
        ('Missing Skills & Keywords', {
            'fields': ('missing_skills', 'missing_keywords'),
            'classes': ('collapse',)
        }),
        ('Suggestions', {
            'fields': ('suggestions',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def resume_title(self, obj):
        return obj.resume.title
    resume_title.short_description = 'Resume'

    def jd_title(self, obj):
        return obj.job_description.title
    jd_title.short_description = 'Job Description'

    def score_display(self, obj):
        score = obj.final_score
        if score >= 80:
            color = '#198754'
        elif score >= 60:
            color = '#0d6efd'
        elif score >= 40:
            color = '#ffc107'
        else:
            color = '#dc3545'
        return format_html(
            '<span style="color:{}; font-weight:bold;">{:.1f}% — {}</span>',
            color, score, obj.get_label()
        )
    score_display.short_description = 'Final Score'
