from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import Scheme, SchemeCategory, SchemeLevel
from .serializers import (
    SchemeListSerializer, SchemeDetailSerializer, EligibilityCheckSerializer,
    EligibilityResultSerializer, SchemeCategorySerializer, SchemeStatsSerializer,
    SchemeSearchSerializer
)


class StandardResultsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class SchemeListView(generics.ListAPIView):
    """
    List government schemes with filtering, search, and pagination
    
    Supports filtering by:
    - level: central, state, district, block, panchayat
    - category: agriculture, education, healthcare, etc.
    - state: specific state name
    - search: searches in scheme name, details, benefits
    - is_active: true/false
    """
    queryset = Scheme.objects.filter(is_active=True)
    serializer_class = SchemeListSerializer
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['level', 'scheme_category', 'state', 'is_active']
    search_fields = ['scheme_name', 'details', 'benefits', 'search_keywords']
    ordering_fields = ['scheme_name', 'created_at', 'level']
    ordering = ['scheme_name']

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                description='Search in scheme name, details, and benefits'
            ),
            OpenApiParameter(
                name='level',
                type=OpenApiTypes.STR,
                enum=['central', 'state', 'district', 'block', 'panchayat']
            ),
            OpenApiParameter(
                name='scheme_category',
                type=OpenApiTypes.STR,
                enum=[choice[0] for choice in SchemeCategory.choices]
            ),
            OpenApiParameter(
                name='state',
                type=OpenApiTypes.STR,
                description='Filter by state name'
            ),
        ],
        examples=[
            OpenApiExample(
                'Search example',
                summary='Search for education schemes',
                description='Find all schemes related to education',
                value={'search': 'education', 'level': 'central'}
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class SchemeDetailView(generics.RetrieveAPIView):
    """
    Get detailed information about a specific scheme
    """
    queryset = Scheme.objects.all()
    serializer_class = SchemeDetailSerializer
    lookup_field = 'slug'

    @extend_schema(
        examples=[
            OpenApiExample(
                'Scheme detail response',
                summary='Complete scheme information',
                description='All details about a specific scheme',
                value={
                    'scheme_id': 'uuid',
                    'scheme_name': 'PM Kisan Samman Nidhi',
                    'slug': 'pm-kisan-samman-nidhi',
                    'details': 'Detailed description...',
                    'benefits': 'Financial assistance...',
                    'eligibility': 'Farmers with landholding...',
                    'level': 'central',
                    'scheme_category': 'agriculture'
                }
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(
    request=EligibilityCheckSerializer,
    responses=EligibilityResultSerializer(many=True),
    examples=[
        OpenApiExample(
            'Eligibility check request',
            summary='Check eligibility for schemes',
            description='Provide user data to check scheme eligibility',
            value={
                'age': 25,
                'gender': 'female',
                'income': 50000,
                'state': 'Karnataka',
                'category': 'general'
            }
        ),
    ]
)
@api_view(['POST'])
def eligibility_check(request):
    """
    Check user eligibility for government schemes
    
    Analyzes user data against scheme eligibility criteria and returns
    matching schemes with confidence scores.
    """
    serializer = EligibilityCheckSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user_data = serializer.validated_data
    eligible_schemes = []
    
    # Get all active schemes
    schemes = Scheme.objects.filter(is_active=True)
    
    # Filter by state if provided
    if 'state' in user_data and user_data['state']:
        schemes = schemes.filter(
            Q(state__icontains=user_data['state']) | Q(level='central')
        )
    
    for scheme in schemes:
        eligibility_result = scheme.check_eligibility_match(user_data)
        
        if eligibility_result['eligible']:
            result_data = {
                'scheme': scheme,
                'eligible': eligibility_result['eligible'],
                'confidence': eligibility_result['confidence'],
                'matches': eligibility_result['matches'],
                'eligibility_text': eligibility_result['eligibility_text']
            }
            eligible_schemes.append(result_data)
    
    # Sort by confidence score (descending)
    eligible_schemes.sort(key=lambda x: x['confidence'], reverse=True)
    
    # Limit to top 20 results
    eligible_schemes = eligible_schemes[:20]
    
    serializer = EligibilityResultSerializer(eligible_schemes, many=True)
    return Response({
        'eligible_schemes': serializer.data,
        'total_found': len(eligible_schemes),
        'user_criteria': user_data
    })


class SchemeDocumentsView(generics.RetrieveAPIView):
    """
    Get required documents for a specific scheme
    """
    queryset = Scheme.objects.all()
    lookup_field = 'slug'

    @extend_schema(
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'scheme_name': {'type': 'string'},
                    'documents': {
                        'type': 'array',
                        'items': {'type': 'string'}
                    },
                    'document_objects': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'document_name': {'type': 'string'},
                                'document_type': {'type': 'string'},
                                'is_mandatory': {'type': 'boolean'}
                            }
                        }
                    }
                }
            }
        }
    )
    def get(self, request, slug):
        scheme = get_object_or_404(Scheme, slug=slug)
        
        documents_list = scheme.get_required_documents_list()
        document_objects = scheme.required_documents.all()
        
        return Response({
            'scheme_name': scheme.scheme_name,
            'scheme_slug': scheme.slug,
            'documents': documents_list,
            'document_objects': [
                {
                    'document_name': doc.document_name,
                    'document_type': doc.document_type,
                    'is_mandatory': doc.is_mandatory,
                    'description': doc.description
                }
                for doc in document_objects
            ],
            'documents_count': len(documents_list) + document_objects.count()
        })


class CategorySchemesView(generics.ListAPIView):
    """
    Get schemes by category
    """
    serializer_class = SchemeListSerializer
    pagination_class = StandardResultsPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                enum=[choice[0] for choice in SchemeCategory.choices]
            ),
        ]
    )
    def get_queryset(self):
        category = self.kwargs['category']
        return Scheme.objects.filter(
            scheme_category=category,
            is_active=True
        ).order_by('scheme_name')


@extend_schema(
    responses=SchemeStatsSerializer,
    examples=[
        OpenApiExample(
            'Statistics response',
            summary='Scheme statistics',
            description='Overview of scheme counts by category and level',
            value={
                'total_schemes': 150,
                'active_schemes': 145,
                'central_schemes': 80,
                'state_schemes': 65,
                'categories': [
                    {'category': 'agriculture', 'category_display': 'Agriculture', 'count': 25},
                    {'category': 'education', 'category_display': 'Education', 'count': 30}
                ]
            }
        ),
    ]
)
@api_view(['GET'])
def scheme_statistics(request):
    """
    Get overview statistics of schemes
    """
    total_schemes = Scheme.objects.count()
    active_schemes = Scheme.objects.filter(is_active=True).count()
    central_schemes = Scheme.objects.filter(level='central').count()
    state_schemes = Scheme.objects.filter(level='state').count()
    
    # Category statistics
    category_stats = []
    for category_code, category_name in SchemeCategory.choices:
        count = Scheme.objects.filter(
            scheme_category=category_code,
            is_active=True
        ).count()
        if count > 0:
            category_stats.append({
                'category': category_code,
                'category_display': category_name,
                'count': count
            })
    
    data = {
        'total_schemes': total_schemes,
        'active_schemes': active_schemes,
        'central_schemes': central_schemes,
        'state_schemes': state_schemes,
        'categories': category_stats
    }
    
    serializer = SchemeStatsSerializer(data)
    return Response(serializer.data)


@extend_schema(
    responses={
        200: {
            'type': 'object',
            'properties': {
                'categories': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'value': {'type': 'string'},
                            'label': {'type': 'string'}
                        }
                    }
                },
                'levels': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'value': {'type': 'string'},
                            'label': {'type': 'string'}
                        }
                    }
                }
            }
        }
    }
)
@api_view(['GET'])
def scheme_filters(request):
    """
    Get available filter options for schemes
    """
    categories = [
        {'value': code, 'label': name}
        for code, name in SchemeCategory.choices
    ]
    
    levels = [
        {'value': code, 'label': name}
        for code, name in SchemeLevel.choices
    ]
    
    # Get unique states from schemes
    states = Scheme.objects.exclude(
        state__isnull=True
    ).exclude(
        state__exact=''
    ).values_list('state', flat=True).distinct().order_by('state')
    
    states_list = [
        {'value': state, 'label': state}
        for state in states
    ]
    
    return Response({
        'categories': categories,
        'levels': levels,
        'states': states_list
    })
