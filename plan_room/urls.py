from django.urls import path
from . import views

urlpatterns = [
    # Browsing
    path('', views.Home.as_view(), name='home'),  # Temporary home view
    path('plans/', views.PlanSetListView.as_view(), name='plan_list'),
    path('search/', views.PlanSetListView.as_view(), name='search'),  # Same view, ?q= param

    # Plan set details & preview
    path('plan/<int:pk>/', views.PlanSetDetailView.as_view(), name='plan_set_detail'),
    path('preview/<int:document_id>/', views.preview_document, name='preview_document'),  # AJAX

    # Access
    path('download/<int:plan_set_id>/', views.download_set, name='download_set'),

    # Auth is handled by allauth, see main urls.py
]