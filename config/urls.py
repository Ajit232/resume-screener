from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # Home page
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    # App URL namespaces
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('jobs/', include('jobs.urls', namespace='jobs')),
    path('resumes/', include('resumes.urls', namespace='resumes')),
    path('analysis/', include('analysis.urls', namespace='analysis')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
