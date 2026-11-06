from django.db import models
from cloudinary.models import CloudinaryField
from django.core.validators import FileExtensionValidator
from django.forms import ValidationError
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from embed_video.fields import EmbedVideoField


# Create your models here.
class WebsiteLogo(models.Model):
    image=models.ImageField(
        upload_to='logo_images',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],
        unique=True, blank=True, null=True
    )
  
    
class WebsiteTitle(models.Model):
    logo=models.ForeignKey(WebsiteLogo, on_delete=models.CASCADE, blank=True, null=True)
    site_title=models.CharField(max_length=100)
    
    
class NavContent(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='nav_content/images/', blank=True)
    nav_paragraph = RichTextUploadingField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)  # Updated for date

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    title = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)  # Updated for date

    def __str__(self):
        return self.title
    
    def get_children(self):
        return SubMenuItem.objects.filter(parent_menuitem=self) if 'SubMenuItem' in globals() else []
    

class SubMenuItem(models.Model):
    parent_menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    subtitle = models.CharField(max_length=100)
    nav_content = models.ForeignKey(NavContent, on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)  # Updated for date

    def __str__(self):
        return self.subtitle  
    
   
class ContactInfo(models.Model):
    address=models.CharField(max_length=150,blank=True, null=True)
    phone=models.CharField(max_length=50, blank=True, null=True)
    email= models.EmailField(max_length=254,blank=True, null=True)
    maplink = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return "Contact Info"
    
    
class SocialMediaLink(models.Model):
    name = models.CharField(max_length=50)
    icon_class = models.CharField(max_length=50)
    link = models.URLField()

    def __str__(self):
        return self.name
    

class HeroImages(models.Model):
    image=models.ImageField(
        upload_to='hero_images',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],
        blank=True, null=True
    )
    hero_title=models.CharField(max_length=100)
    hero_paragraph = RichTextUploadingField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Hero Image {self.hero_title}"
    
# Define a separate model for Group with an image field
class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='group_images/', blank=True, null=True)

    def __str__(self):
        return self.display_name

# Remove the tuple Group and use ForeignKey in related models

class Projects(models.Model):
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, null=True)  # Group for categorization
    title = models.CharField(max_length=255)  # Title of the project
    description = RichTextUploadingField()  # Detailed information about the project
    created_at = models.DateTimeField(auto_now_add=True)  # Upload time

    def __str__(self):
        return f"{self.group.name if self.group else 'No Group'} - {self.title}"
    
    
class ProjectImage(models.Model):
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(
        upload_to='projects/gallery/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])]
    )
    caption = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'uploaded_at']

    def __str__(self):
        return f"Image for {self.project.title}"


class CompanyResource(models.Model):

    CATEGORY_CHOICES = [
        ('technical', 'Technical Documents'),
        ('safety', 'Safety & Compliance'),
        ('support', 'Support & Guidance'),
    ]
    title = models.CharField(max_length=255)  # Title of the resource
    description = RichTextUploadingField()  # Detailed information about the resource
    file = models.FileField(upload_to='resources/files/', blank=True, null=True)  # Optional file upload
    image = models.ImageField(upload_to='resources/img/', blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)  # Category of the resource
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the resource was added

    def __str__(self):
        return f"{self.title}"
    
    
def past_datetime_validator(value):
    if value >= timezone.now():
        raise ValidationError('Date and time can''t be in the future.')
class Our_Mission_Vision_Statement(models.Model):
    image = models.ImageField(upload_to='founder_image/', blank=True)
    founder_fullname = models.CharField(max_length=255, blank=True, null=True)
    founder_title = models.CharField(max_length=255, blank=True, null=True)
    founder_quote = models.CharField(max_length=255, blank=True, null=True)
    history=RichTextUploadingField(blank=True, null=True) 
    mission_statement = RichTextUploadingField(blank=True, null=True) 
    vision_statement = RichTextUploadingField(blank=True, null=True)  
    our_values = RichTextUploadingField(blank=True, null=True)  
    our_purpose = RichTextUploadingField(blank=True, null=True) 
    slogan=models.TextField(max_length=250, blank=True, null=True)
    year_founded_est = models.DateTimeField(blank=True, null=True, validators=[past_datetime_validator])  # Apply the custom validator
    date = models.DateTimeField(auto_now_add=True)  # Updated for date
    
    def __str__(self):
        return "Mission And Vision Statement"
    
    
class Services(models.Model):
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, null=True)  # Group for categorization
    title = models.CharField(max_length=255)  # Title of the project
    description = RichTextUploadingField()  # Detailed information about the project
    date = models.DateTimeField(auto_now_add=True)  # Updated for date
    image = models.ImageField(upload_to='services/images/', blank=True) 
    
    def __str__(self):
        return f"{self.group.name if self.group else 'No Group'} - {self.title}"
    
    
class Stat(models.Model):
    title = models.CharField(max_length=255)  # Title of the stat
    value = models.PositiveIntegerField()  # Numeric value of the stat

    def __str__(self):
        return f"{self.title} ({self.value})"
    
    
class Team(models.Model):
    image = models.ImageField(
        upload_to='team_images',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],
        unique=True, blank=True, null=True)
    fullname = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True, null=True)
    bio = RichTextUploadingField(blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)  # Use default=timezone.now() for current date

    def __str__(self):
        return self.fullname

    class Meta:
        ordering = ['created']  # Order objects by created date descending (oldest first)
        

    
class ClientType(models.Model):
    image = models.ImageField(
        upload_to='team_images',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],
        unique=True, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    description = RichTextUploadingField(blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)  # Use default=timezone.now() for current date

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['created']  # Order objects by created date descending (oldest first)
    
    
class ClientTestimonial(models.Model):
    image = models.ImageField(upload_to='testimonial_images', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])], blank=True, null=True)
    fullname = models.CharField(max_length=255)
    saying = models.TextField()
    location=models.CharField(max_length=250)
    published_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fullname
    
    class Meta:
        ordering = ['-published_date']  # Order by published_date in descending order
    
    
class ClientSector(models.Model):
    image = models.ImageField(
        upload_to='client_sector_images',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],
        blank=True, null=True
    )
    title = models.CharField(max_length=100)
    description = RichTextUploadingField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)  # Updated for date

    def __str__(self):
        return self.title
    
    
class BlogNews_Updates(models.Model):
    image = models.ImageField(upload_to='blog_news_images', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])], blank=True, null=True)
    title = models.CharField(max_length=255)
    content = RichTextUploadingField()
    author = models.CharField(max_length=255)
    published_date = models.DateTimeField(auto_now_add=True)
    tag = models.CharField(max_length=255)

    def __str__(self):
        return self.title
    
    
class PartnersAndSponsors(models.Model):
    logo = models.ImageField(upload_to='images/partners_images', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])], blank=True, null=True)
    name = models.CharField(max_length=255)
    link = models.URLField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    
class BackgroundImg(models.Model):
    image=models.ImageField(
        upload_to='bg_images',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],
        unique=True, blank=True, null=True
    )
    def __str__(self):
        return f"Background Image {self.pk}"

    
    
def future_datetime_validator(value):
    if value <= timezone.now():
        raise ValidationError('Date and time must be in the future.')
class Next_Event(models.Model):
    image = models.ImageField(upload_to='team_images', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])], blank=True, null=True)
    event_title = models.CharField(max_length=100, blank=True, null=True)
    about_event = RichTextUploadingField(blank=True, null=True)
    when = models.DateTimeField(blank=True, null=True, validators=[future_datetime_validator])  # Apply the custom validator
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self) -> str:
        return self.event_title if self.event_title else "Unnamed Event"
    
    
    
class Gallery(models.Model):
    image=models.ImageField(upload_to='galleries', 
    validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])], 
    unique=True, blank=True, null=True)
    when = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Gallery Image {self.pk}"
    
    
class VideoFrame(models.Model):
    video_title=models.CharField(max_length=100, blank=True, null=True)
    video=EmbedVideoField()
    
    def __str__(self):
        return self.video_title
    
    
class FAQ(models.Model):
    question = models.CharField(max_length=250,blank=True, null=True)
    answer = models.CharField(max_length=250,blank=True, null=True)

    def __str__(self):
        return self.question
    
    
class ContactFormEntry(models.Model):
    name=models.CharField(max_length=255)
    phone=models.CharField(max_length=255)
    email=models.EmailField()
    subject=models.CharField(max_length=255)
    message=RichTextUploadingField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.subject
    
    
class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    def __str__(self):
        return f"Message from {self.name}"
    
    
class Subscriber(models.Model):
    subscriber_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)  # Mark inactive until confirmation
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    
    
    
# Video upload model for secure video uploads (Cloudinary or local)
class VideoUpload(models.Model):
    # To use Cloudinary, uncomment the CloudinaryField and related logic below and comment out FileField
    # from cloudinary.models import CloudinaryField
    # COMPRESSION_CHOICES = [ ... ]
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name='videos', blank=True, null=True, help_text="Associate this video with a project (optional)")
    title = models.CharField(max_length=255)
    video = models.FileField(
        upload_to='videos/',
        validators=[FileExtensionValidator(['mp4', 'mov', 'avi', 'mkv'])],
        blank=True,
        null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Video Upload"
        verbose_name_plural = "Video Uploads"



class CompanyHighlight(models.Model):
    text = models.CharField(max_length=255, help_text="e.g. '100% Liberian Owned & Managed'")
    icon_class = models.CharField(max_length=100, default='fas fa-check-circle', help_text="FontAwesome class e.g. 'fas fa-check-circle'")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text
