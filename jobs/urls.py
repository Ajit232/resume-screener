from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('upload/', views.upload_jd_view, name='upload'),
    path('list/', views.list_jd_view, name='list'),
    path('<int:pk>/', views.jd_detail_view, name='detail'),
    path('<int:pk>/delete/', views.delete_jd_view, name='delete'),
]
