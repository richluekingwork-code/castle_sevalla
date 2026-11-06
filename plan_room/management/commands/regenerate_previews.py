from django.core.management.base import BaseCommand
from plan_room.models import PlanDocument
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Regenerate preview PDFs for all documents'

    def handle(self, *args, **kwargs):
        documents = PlanDocument.objects.all()
        self.stdout.write(f"Found {documents.count()} documents")
        
        # Clear existing previews
        preview_dir = os.path.join(settings.MEDIA_ROOT, 'plan_previews')
        if os.path.exists(preview_dir):
            for file in os.listdir(preview_dir):
                if file.endswith('.pdf'):
                    os.remove(os.path.join(preview_dir, file))
        
        for document in documents:
            self.stdout.write(f"\nRegenerating preview for Document {document.id}: {document}")
            try:
                # Clear existing preview
                if document.preview_pdf:
                    document.preview_pdf.delete()
                
                # Force preview regeneration
                import PyPDF2
                from io import BytesIO
                
                # Read full PDF
                full_pdf = PyPDF2.PdfReader(document.pdf_file.open())
                preview_writer = PyPDF2.PdfWriter()
                num_pages = min(document.plan_set.preview_pages, len(full_pdf.pages))
                
                # Add first N pages to preview
                for page_num in range(num_pages):
                    preview_writer.add_page(full_pdf.pages[page_num])
                
                # Save to BytesIO and upload
                buffer = BytesIO()
                preview_writer.write(buffer)
                buffer.seek(0)
                
                preview_name = f"preview_{os.path.basename(document.pdf_file.name)}"
                document.preview_pdf.save(preview_name, buffer, save=True)
                
                self.stdout.write(self.style.SUCCESS(f"Successfully regenerated preview as {preview_name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error generating preview: {e}"))