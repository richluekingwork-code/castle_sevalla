from django.urls import path
from .views import (
    HomeView, AboutView, ServicesView, ProjectsView, ContactView
)

app_name = 'castle_site'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('services/', ServicesView.as_view(), name='services'),
    path('projects/', ProjectsView.as_view(), name='projects'),
    path('contact/', ContactView.as_view(), name='contact'),
]
