from django.urls import path
from . import views

app_name = 'schemes'

urlpatterns = [
    # Scheme listing and details
    path('', views.SchemeListView.as_view(), name='scheme-list'),
    
    # Eligibility check
    path('eligibility-check/', views.eligibility_check, name='eligibility-check'),
    
    # Statistics and filters (MUST come before detail view)
    path('stats/', views.scheme_statistics, name='scheme-statistics'),
    path('filters/', views.scheme_filters, name='scheme-filters'),
    
    # Category-based schemes
    path('categories/<str:category>/', views.CategorySchemesView.as_view(), name='category-schemes'),
    
    # Documents
    path('<slug:slug>/documents/', views.SchemeDocumentsView.as_view(), name='scheme-documents'),
    
    # Scheme detail (MUST come last due to slug pattern)
    path('<slug:slug>/', views.SchemeDetailView.as_view(), name='scheme-detail'),
]
