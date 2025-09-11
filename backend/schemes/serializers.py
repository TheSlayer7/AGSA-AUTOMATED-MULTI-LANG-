from rest_framework import serializers
from .models import Scheme, SchemeDocument, SchemeCategory, SchemeLevel


class SchemeDocumentSerializer(serializers.ModelSerializer):
    """Serializer for individual scheme documents"""
    
    class Meta:
        model = SchemeDocument
        fields = [
            'document_name', 'document_type', 'is_mandatory', 'description'
        ]


class SchemeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for scheme listings"""
    
    category_display = serializers.CharField(source='get_scheme_category_display', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Scheme
        fields = [
            'scheme_id', 'scheme_name', 'slug', 'level', 'level_display',
            'scheme_category', 'category_display', 'state', 'is_active',
            'created_at', 'document_count'
        ]
    
    def get_document_count(self, obj):
        """Count of required documents"""
        docs = obj.get_required_documents_list()
        return len(docs)


class SchemeDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual schemes"""
    
    category_display = serializers.CharField(source='get_scheme_category_display', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    required_documents_list = serializers.SerializerMethodField()
    document_objects = SchemeDocumentSerializer(source='required_documents', many=True, read_only=True)
    
    class Meta:
        model = Scheme
        fields = [
            'scheme_id', 'scheme_name', 'slug', 'details', 'benefits',
            'eligibility', 'application', 'documents', 'level', 'level_display',
            'scheme_category', 'category_display', 'state', 'ministry_department',
            'launch_date', 'website_url', 'is_active', 'created_at', 'updated_at',
            'required_documents_list', 'document_objects'
        ]
    
    def get_required_documents_list(self, obj):
        """Parse documents into a clean list"""
        return obj.get_required_documents_list()


class EligibilityCheckSerializer(serializers.Serializer):
    """Serializer for eligibility check input"""
    
    age = serializers.IntegerField(required=False, min_value=0, max_value=120)
    gender = serializers.ChoiceField(
        choices=['male', 'female', 'other'],
        required=False
    )
    income = serializers.IntegerField(required=False, min_value=0)
    state = serializers.CharField(max_length=100, required=False)
    category = serializers.ChoiceField(
        choices=['general', 'obc', 'sc', 'st', 'ews'],
        required=False
    )
    occupation = serializers.CharField(max_length=100, required=False)
    education = serializers.CharField(max_length=100, required=False)
    is_rural = serializers.BooleanField(required=False)
    
    def validate(self, data):
        """Ensure at least one criteria is provided"""
        if not any(data.values()):
            raise serializers.ValidationError(
                "At least one eligibility criteria must be provided"
            )
        return data


class EligibilityResultSerializer(serializers.Serializer):
    """Serializer for eligibility check results"""
    
    scheme = SchemeListSerializer()
    eligible = serializers.BooleanField()
    confidence = serializers.FloatField()
    matches = serializers.ListField(child=serializers.CharField())
    eligibility_text = serializers.CharField()


class SchemeCategorySerializer(serializers.Serializer):
    """Serializer for scheme categories"""
    
    category = serializers.CharField()
    category_display = serializers.CharField()
    count = serializers.IntegerField()


class SchemeStatsSerializer(serializers.Serializer):
    """Serializer for scheme statistics"""
    
    total_schemes = serializers.IntegerField()
    active_schemes = serializers.IntegerField()
    central_schemes = serializers.IntegerField()
    state_schemes = serializers.IntegerField()
    categories = SchemeCategorySerializer(many=True)


class SchemeSearchSerializer(serializers.Serializer):
    """Serializer for search parameters"""
    
    search = serializers.CharField(required=False, allow_blank=True)
    level = serializers.ChoiceField(
        choices=SchemeLevel.choices,
        required=False,
        allow_blank=True
    )
    category = serializers.ChoiceField(
        choices=SchemeCategory.choices,
        required=False,
        allow_blank=True
    )
    state = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)
    ordering = serializers.ChoiceField(
        choices=[
            'scheme_name', '-scheme_name',
            'created_at', '-created_at',
            'level', '-level'
        ],
        required=False,
        default='scheme_name'
    )


class SchemeImportSerializer(serializers.Serializer):
    """Serializer for scheme import from CSV/JSON"""
    
    file = serializers.FileField()
    format = serializers.ChoiceField(choices=['csv', 'json'])
    overwrite = serializers.BooleanField(default=False)
    
    def validate_file(self, value):
        """Validate file format"""
        if not value.name.endswith(('.csv', '.json')):
            raise serializers.ValidationError(
                "File must be in CSV or JSON format"
            )
        return value
