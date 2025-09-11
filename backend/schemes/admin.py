from django.contrib import admin
from django.utils.html import format_html
from .models import Scheme, SchemeDocument


@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    list_display = [
        'scheme_name', 'level', 'scheme_category', 'state', 
        'is_active', 'created_at', 'document_count'
    ]
    list_filter = [
        'level', 'scheme_category', 'is_active', 'state', 'created_at'
    ]
    search_fields = [
        'scheme_name', 'details', 'benefits', 'eligibility', 'search_keywords'
    ]
    readonly_fields = ['scheme_id', 'slug', 'created_at', 'updated_at', 'search_keywords']
    prepopulated_fields = {'slug': ('scheme_name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('scheme_name', 'slug', 'scheme_id', 'is_active')
        }),
        ('Classification', {
            'fields': ('level', 'scheme_category', 'state', 'ministry_department')
        }),
        ('Content', {
            'fields': ('details', 'benefits', 'eligibility', 'application', 'documents'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('launch_date', 'website_url', 'search_keywords'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def document_count(self, obj):
        count = len(obj.get_required_documents_list())
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if count > 0 else 'red',
            count
        )
    document_count.short_description = 'Documents'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
    
    actions = ['make_active', 'make_inactive', 'regenerate_keywords']
    
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} schemes marked as active.')
    make_active.short_description = "Mark selected schemes as active"
    
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} schemes marked as inactive.')
    make_inactive.short_description = "Mark selected schemes as inactive"
    
    def regenerate_keywords(self, request, queryset):
        updated = 0
        for scheme in queryset:
            scheme.search_keywords = ''  # Clear to regenerate
            scheme.save()
            updated += 1
        self.message_user(request, f'Regenerated keywords for {updated} schemes.')
    regenerate_keywords.short_description = "Regenerate search keywords"


@admin.register(SchemeDocument)
class SchemeDocumentAdmin(admin.ModelAdmin):
    list_display = ['document_name', 'scheme', 'document_type', 'is_mandatory']
    list_filter = ['document_type', 'is_mandatory']
    search_fields = ['document_name', 'scheme__scheme_name']
    autocomplete_fields = ['scheme']
