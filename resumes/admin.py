from django.contrib import admin
from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'version',
        'is_optimized', 'word_count_display',
        'created_at'
    ]
    search_fields = ['title', 'raw_text', 'user__username']
    list_filter = ['is_optimized', 'created_at']
    readonly_fields = ['version', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'title', 'file')
        }),
        ('Content', {
            'fields': ('raw_text',)
        }),
        ('Version Info', {
            'fields': ('version', 'is_optimized', 'parent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def word_count_display(self, obj):
        return obj.word_count()
    word_count_display.short_description = 'Words'
