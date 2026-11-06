from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
import PyPDF2  # For preview generation
from io import BytesIO
import os

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_client = models.BooleanField(default=False)  # For client-only access
    verified_at = models.DateTimeField(null=True, blank=True)  # Timestamp if verified (e.g., via email)

    def __str__(self):
        return f"Profile for {self.user.email}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

# Auto-create profile on user signup
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)  # Auto-generated
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['slug'])]

class PlanSet(models.Model):
    ACCESS_CHOICES = [
        ('free', 'Free'),
        ('clients', 'Clients Only'),
    ]

    title = models.CharField(max_length=200)
    prepared_by = models.CharField(max_length=100, default="Castle General Group")  # Customize as needed
    cover_image = models.ImageField(upload_to='plan_covers/', blank=True, null=True)
    description = models.TextField()
    categories = models.ManyToManyField(Category, related_name='plan_sets')
    access_type = models.CharField(max_length=20, choices=ACCESS_CHOICES, default='clients')
    preview_pages = models.PositiveIntegerField(default=10)  # Pages to extract for preview
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['title', 'access_type'])]

class PlanDocument(models.Model):
    plan_set = models.ForeignKey(PlanSet, on_delete=models.CASCADE, related_name='documents')
    document_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200, blank=True)  # Optional per-document title
    pdf_file = models.FileField(upload_to='plan_documents/')
    preview_pdf = models.FileField(upload_to='plan_previews/', blank=True)  # Auto-generated

    def __str__(self):
        return f"{self.plan_set.title} - Document {self.document_number}"

    class Meta:
        ordering = ['document_number']
        unique_together = ['plan_set', 'document_number']  # Prevent duplicates

    def generate_preview(self):
        # Read full PDF
        full_pdf = PyPDF2.PdfReader(self.pdf_file.open())
        preview_writer = PyPDF2.PdfWriter()
        num_pages = min(self.plan_set.preview_pages, len(full_pdf.pages))

        # Add first N pages to preview
        for page_num in range(num_pages):
            preview_writer.add_page(full_pdf.pages[page_num])

        # Save to BytesIO and upload
        buffer = BytesIO()
        preview_writer.write(buffer)
        buffer.seek(0)
        self.preview_pdf.save(f"preview_{os.path.basename(self.pdf_file.name)}", buffer)

# Signal to auto-generate preview PDF on document save
@receiver(post_save, sender=PlanDocument)
def generate_preview_pdf(sender, instance, **kwargs):
    if instance.pdf_file and not instance.preview_pdf:
        try:
            instance.generate_preview()
        except Exception as e:
            print(f"Error generating preview: {e}")  # Log in prod
