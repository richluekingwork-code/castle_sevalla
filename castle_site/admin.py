from django.contrib import admin
from .models import (
    HeroImages, Services, Projects, ProjectImage, Stat, ClientTestimonial,
    Team, PartnersAndSponsors, BackgroundImg, Our_Mission_Vision_Statement,
    BlogNews_Updates, ContactInfo, Group, WebsiteLogo, WebsiteTitle,
    NavContent, MenuItem, SubMenuItem, CompanyResource,
    ClientType, ClientSector, Next_Event, Gallery, VideoFrame,
    FAQ, ContactFormEntry, ContactMessage, Subscriber,
    VideoUpload, CompanyHighlight, SocialMediaLink
)

# Admin Site Customization
admin.site.site_header = "Castle General Group Admin"
admin.site.site_title = "Castle CMS"
admin.site.index_title = "Welcome to Castle General Group Management"

# Register your models here.

@admin.register(HeroImages)
class HeroImagesAdmin(admin.ModelAdmin):
    list_display = ('hero_title', 'submitted_at')

@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'date')
    list_filter = ('group',)

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 3
    fields = ('image', 'caption', 'order')


@admin.register(Projects)
class ProjectsAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'created_at')
    list_filter = ('group',)
    inlines = [ProjectImageInline]

    class Media:
        js = ('js/multi_upload.js',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'title', 'created')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message')

@admin.register(ContactFormEntry)
class ContactFormEntryAdmin(admin.ModelAdmin):
    list_display = ('subject', 'email', 'phone', 'submitted_at')

# Simple Registrations
admin.site.register(Stat)
admin.site.register(ClientTestimonial)
admin.site.register(PartnersAndSponsors)
admin.site.register(BackgroundImg)
admin.site.register(Our_Mission_Vision_Statement)
admin.site.register(BlogNews_Updates)
admin.site.register(ContactInfo)
admin.site.register(Group)
admin.site.register(WebsiteLogo)
admin.site.register(WebsiteTitle)
admin.site.register(NavContent)
admin.site.register(MenuItem)
admin.site.register(SubMenuItem)
admin.site.register(CompanyResource)
admin.site.register(ClientType)
admin.site.register(ClientSector)
admin.site.register(Next_Event)
admin.site.register(Gallery)
admin.site.register(VideoFrame)
admin.site.register(FAQ)
admin.site.register(Subscriber)
admin.site.register(VideoUpload)
admin.site.register(CompanyHighlight)
admin.site.register(SocialMediaLink)