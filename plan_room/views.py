from django.utils.text import slugify
from django.http import HttpResponse
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import PlanSet, PlanDocument, Category
from .forms import SearchForm
import zipfile
from io import BytesIO


class Home(View):
    def get(self, request):
        return HttpResponse("Hello, this is the Home view for testing.")


class PlanSetListView(ListView):
    model = PlanSet
    template_name = 'plan_room/list.html'  # Grid of plan sets
    context_object_name = 'plan_sets'
    paginate_by = 12  # Modern pagination

    def get_queryset(self):
        queryset = PlanSet.objects.all()
        query = self.request.GET.get('q')
        category = self.request.GET.get('category')
        access_type = self.request.GET.get('access')
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))
        if category:
            queryset = queryset.filter(categories__slug=category)
        if access_type:
            queryset = queryset.filter(access_type=access_type)
        return queryset.distinct().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()  # For filters
        context['search_form'] = SearchForm(self.request.GET)
        context['access_types'] = PlanSet.ACCESS_CHOICES
        return context

class PlanSetDetailView(DetailView):
    model = PlanSet
    template_name = 'plan_room/details.html'  # Hero, description, documents, preview
    context_object_name = 'plan_set'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plan_set = context['plan_set']
        context['documents'] = plan_set.documents.all()  # Document list
        context['preview_documents'] = plan_set.documents.filter(preview_pdf__isnull=False)[:2]  # First 2 for teaser
        context['feedback_url'] = f"mailto:{plan_set.prepared_by}@example.com"  # Feedback email
        return context

@login_required
def download_set(request, plan_set_id):
    plan_set = get_object_or_404(PlanSet, id=plan_set_id)
    if plan_set.access_type != 'free':
        messages.error(request, 'Access denied.')
        return redirect('plan_set_detail', pk=plan_set.id)

    filename = slugify(plan_set.title) or f'plan-set-{plan_set.id}'

    # Create ZIP of all documents. Files are read through storage so this works on Cloudinary.
    buffer = BytesIO()
    try:
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for document in plan_set.documents.all():
                if document.pdf_file:
                    with document.pdf_file.open('rb') as pdf:
                        zip_file.writestr(f"{filename}_Doc{document.document_number}.pdf", pdf.read())
    except OSError as e:
        print(f"Error building download for plan set {plan_set.id}: {e}")  # Log in prod
        messages.error(request, 'These files could not be downloaded right now. Please try again later.')
        return redirect('plan_set_detail', pk=plan_set.id)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{filename}.zip"'
    return response

def preview_document(request, document_id):
    # AJAX for modal preview
    document = get_object_or_404(PlanDocument, id=document_id)

    if document.plan_set.access_type == 'free':
        pdf = document.pdf_file
    else:
        if not document.preview_pdf and document.pdf_file:
            try:
                document.generate_preview()
            except Exception as e:
                print(f"Error generating preview: {e}")  # Log in prod
                return JsonResponse({'error': 'Error generating preview.'}, status=500)
        pdf = document.preview_pdf

    if not pdf:
        return JsonResponse({'error': 'No preview available.'}, status=404)

    return JsonResponse({'pdf_url': pdf.url})
