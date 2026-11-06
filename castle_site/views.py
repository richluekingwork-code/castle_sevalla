from django.shortcuts import render
from django.views.generic import TemplateView, ListView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import (
    HeroImages, Services, Projects, Stat, ClientTestimonial, 
    Team, PartnersAndSponsors, BackgroundImg, Our_Mission_Vision_Statement,
    BlogNews_Updates, ContactInfo, ContactFormEntry, Group,
    CompanyHighlight, SocialMediaLink, WebsiteLogo
)
from .forms import ContactForm # Assuming a ContactForm exists or I will create one


class ContextMixin:
    """Mixin to add common context like branding and contact info to all views"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_info'] = ContactInfo.objects.first()
        context['logo'] = WebsiteLogo.objects.first() if 'WebsiteLogo' in globals() else None
        context['services_list'] = Services.objects.all()[:5] # For Footer
        context['social_links'] = SocialMediaLink.objects.all()
        return context

class HomeView(ContextMixin, TemplateView):
    template_name = "castle_site/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch data for the landing page
        context['hero_images'] = HeroImages.objects.order_by('-submitted_at')
        context['services'] = Services.objects.all()[:6]
        context['projects'] = Projects.objects.order_by('-created_at')[:6]
        context['stats'] = Stat.objects.all()
        context['testimonials'] = ClientTestimonial.objects.order_by('-published_date')
        context['team'] = Team.objects.all()[:4]
        context['partners'] = PartnersAndSponsors.objects.all()
        context['latest_news'] = BlogNews_Updates.objects.order_by('-published_date')[:3]
        context['about_info'] = Our_Mission_Vision_Statement.objects.first()
        context['highlights'] = CompanyHighlight.objects.all() # "Who We Are" bullets
        return context


class AboutView(ContextMixin, TemplateView):
    template_name = "castle_site/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['about'] = Our_Mission_Vision_Statement.objects.first()
        context['team'] = Team.objects.all()
        context['partners'] = PartnersAndSponsors.objects.all()
        context['highlights'] = CompanyHighlight.objects.all()
        return context

class ServicesView(ContextMixin, ListView):
    model = Services
    template_name = "castle_site/services.html"
    context_object_name = 'services'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.all() 
        return context

class ProjectsView(ContextMixin, ListView):
    model = Projects
    template_name = "castle_site/projects.html"
    context_object_name = 'projects'
    ordering = ['-created_at']

    def get_queryset(self):
        return Projects.objects.prefetch_related('gallery_images').order_by('-created_at')

class ContactView(ContextMixin, FormView):
    template_name = "castle_site/contact.html"
    form_class = ContactForm # I need to ensure this form exists in forms.py
    success_url = reverse_lazy('castle_site:contact')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_info'] = ContactInfo.objects.first()
        return context

    def form_valid(self, form):
        # Save the contact message using the model form
        form.save()
        messages.success(self.request, "Your message has been sent successfully!")
        return super().form_valid(form)
