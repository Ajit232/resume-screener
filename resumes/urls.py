from django.urls import path
from . import views

app_name = 'resumes'

urlpatterns = [
    path('upload/',              views.upload_resume_view,  name='upload'),
    path('list/',                views.list_resumes_view,   name='list'),
    path('<int:pk>/',            views.resume_detail_view,  name='detail'),
    path('<int:pk>/edit/',       views.resume_editor_view,  name='editor'),
    path('<int:pk>/delete/',     views.delete_resume_view,  name='delete'),

    # Export routes
    path('<int:pk>/export/ats/',    views.export_ats_view,    name='export_ats'),
    path('<int:pk>/export/latex/',  views.export_latex_view,  name='export_latex'),
    path('<int:pk>/export/styled/', views.export_styled_view, name='export_styled'),
]
