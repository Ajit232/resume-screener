from django.contrib import admin
from .models import JobDescription


@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'company', 'user',
        'skill_count', 'keyword_count',
        'experience_required', 'education_required',
        'created_at'
    ]
    search_fields = ['title', 'company', 'raw_text', 'user__username']
    list_filter = ['education_required', 'created_at']
    readonly_fields = ['parsed_skills', 'parsed_keywords', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'title', 'company', 'file')
        }),
        ('Content', {
            'fields': ('raw_text',)
        }),
        ('Requirements', {
            'fields': ('experience_required', 'education_required')
        }),
        ('Parsed NLP Data', {
            'fields': ('parsed_skills', 'parsed_keywords'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def skill_count(self, obj):
        return len(obj.parsed_skills)
    skill_count.short_description = 'Skills'

    def keyword_count(self, obj):
        return len(obj.parsed_keywords)
    keyword_count.short_description = 'Keywords'
