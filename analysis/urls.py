from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    path('run/', views.run_analysis_view, name='run'),
    path('<int:pk>/', views.analysis_result_view, name='result'),
    path('history/', views.analysis_history_view, name='history'),
    path('<int:pk>/delete/', views.delete_analysis_view, name='delete'),
]
