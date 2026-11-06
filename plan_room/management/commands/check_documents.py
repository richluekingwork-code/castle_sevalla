from django.core.management.base import BaseCommand
from plan_room.models import PlanDocument
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Check PlanDocument records and their associated files'

    def handle(self, *args, **kwargs):
        documents = PlanDocument.objects.all()
        self.stdout.write(f"Found {documents.count()} documents")
        
        for document in documents:
            self.stdout.write(f"\nDocument {document.id}: {document}")
            
            # Check PDF file
            if document.pdf_file:
                pdf_path = os.path.join(settings.MEDIA_ROOT, str(document.pdf_file))
                if os.path.exists(pdf_path):
                    self.stdout.write(self.style.SUCCESS(f"PDF exists at {pdf_path}"))
                else:
                    self.stdout.write(self.style.ERROR(f"PDF missing at {pdf_path}"))
            else:
                self.stdout.write(self.style.WARNING("No PDF file assigned"))
            
            # Check preview PDF
            if document.preview_pdf:
                preview_path = os.path.join(settings.MEDIA_ROOT, str(document.preview_pdf))
                if os.path.exists(preview_path):
                    self.stdout.write(self.style.SUCCESS(f"Preview exists at {preview_path}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Preview missing at {preview_path}"))
            else:
                self.stdout.write(self.style.WARNING("No preview PDF assigned"))