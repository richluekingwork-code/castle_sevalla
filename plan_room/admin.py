from django.contrib import admin
from .models import UserProfile, Category, PlanSet, PlanDocument

class PlanDocumentInline(admin.TabularInline):
    model = PlanDocument
    extra = 1  # Easy adding documents inline

@admin.register(PlanSet)
class PlanSetAdmin(admin.ModelAdmin):
    inlines = [PlanDocumentInline]
    list_display = ('title', 'prepared_by', 'access_type')
    search_fields = ('title', 'description')
    filter_horizontal = ('categories',)  # Nice UI for ManyToMany

admin.site.register([UserProfile, Category])




