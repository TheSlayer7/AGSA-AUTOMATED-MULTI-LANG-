from django.db import models
from django.utils.text import slugify
from django.core.validators import MinLengthValidator
import uuid


class SchemeCategory(models.TextChoices):
    """Predefined categories for government schemes"""
    AGRICULTURE = 'agriculture', 'Agriculture'
    EDUCATION = 'education', 'Education'
    HEALTHCARE = 'healthcare', 'Healthcare'
    EMPLOYMENT = 'employment', 'Employment'
    WOMEN_CHILD = 'women_child', 'Women & Child Development'
    RURAL_DEVELOPMENT = 'rural_development', 'Rural Development'
    HOUSING = 'housing', 'Housing'
    FINANCIAL_INCLUSION = 'financial_inclusion', 'Financial Inclusion'
    DISABILITY = 'disability', 'Disability Welfare'
    ELDERLY = 'elderly', 'Elderly Welfare'
    MINORITY = 'minority', 'Minority Affairs'
    TRIBAL = 'tribal', 'Tribal Affairs'
    SKILL_DEVELOPMENT = 'skill_development', 'Skill Development'
    ENVIRONMENT = 'environment', 'Environment'
    TRANSPORT = 'transport', 'Transport'
    SOCIAL_WELFARE = 'social_welfare', 'Social Welfare'
    OTHER = 'other', 'Other'


class SchemeLevel(models.TextChoices):
    """Government levels offering schemes"""
    CENTRAL = 'central', 'Central Government'
    STATE = 'state', 'State Government'
    DISTRICT = 'district', 'District Level'
    BLOCK = 'block', 'Block Level'
    PANCHAYAT = 'panchayat', 'Panchayat Level'


class Scheme(models.Model):
    """Government scheme model with comprehensive information"""
    
    # Basic Information
    scheme_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    scheme_name = models.CharField(
        max_length=500, 
        validators=[MinLengthValidator(3)],
        help_text="Official name of the scheme"
    )
    slug = models.SlugField(
        max_length=200, 
        unique=True, 
        blank=True,
        help_text="URL-friendly version of scheme name"
    )
    
    # Content Fields
    details = models.TextField(
        blank=True, 
        null=True,
        help_text="Detailed description of the scheme"
    )
    benefits = models.TextField(
        blank=True, 
        null=True,
        help_text="Benefits provided by the scheme"
    )
    eligibility = models.TextField(
        blank=True, 
        null=True,
        help_text="Eligibility criteria for the scheme"
    )
    application = models.TextField(
        blank=True, 
        null=True,
        help_text="Application process and procedure"
    )
    documents = models.TextField(
        blank=True, 
        null=True,
        help_text="Required documents for application"
    )
    
    # Classification
    level = models.CharField(
        max_length=20,
        choices=SchemeLevel.choices,
        default=SchemeLevel.CENTRAL,
        help_text="Government level offering this scheme"
    )
    scheme_category = models.CharField(
        max_length=30,
        choices=SchemeCategory.choices,
        default=SchemeCategory.OTHER,
        help_text="Category of the scheme"
    )
    
    # Additional Fields
    state = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Specific state (for state-level schemes)"
    )
    ministry_department = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Ministry or department managing the scheme"
    )
    launch_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date when scheme was launched"
    )
    website_url = models.URLField(
        blank=True,
        null=True,
        help_text="Official website for the scheme"
    )
    
    # Status and Metadata
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the scheme is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Search optimization
    search_keywords = models.TextField(
        blank=True,
        help_text="Additional keywords for search optimization"
    )

    class Meta:
        ordering = ['scheme_name']
        indexes = [
            models.Index(fields=['level']),
            models.Index(fields=['scheme_category']),
            models.Index(fields=['state']),
            models.Index(fields=['is_active']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.scheme_name

    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided"""
        if not self.slug:
            base_slug = slugify(self.scheme_name)
            slug = base_slug
            counter = 1
            while Scheme.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Generate search keywords
        if not self.search_keywords:
            keywords = []
            if self.scheme_name:
                keywords.extend(self.scheme_name.lower().split())
            if self.details:
                keywords.extend([word for word in self.details.lower().split() if len(word) > 3])
            if self.benefits:
                keywords.extend([word for word in self.benefits.lower().split() if len(word) > 3])
            
            # Remove duplicates and join
            self.search_keywords = ' '.join(set(keywords))
        
        super().save(*args, **kwargs)

    def get_required_documents_list(self):
        """Parse documents field into a list"""
        if not self.documents:
            return []
        
        # Split by common separators and clean
        docs = []
        for separator in ['\n', '•', '-', '*', '1.', '2.', '3.', '4.', '5.']:
            if separator in self.documents:
                docs = [doc.strip() for doc in self.documents.split(separator) if doc.strip()]
                break
        
        if not docs:
            docs = [self.documents.strip()]
        
        return [doc for doc in docs if doc and len(doc) > 3]

    def check_eligibility_match(self, user_data):
        """Check if user matches eligibility criteria"""
        if not self.eligibility:
            return {'eligible': False, 'reason': 'No eligibility criteria defined'}
        
        eligibility_text = self.eligibility.lower()
        matches = []
        reasons = []
        
        # Age-based matching
        if 'age' in user_data:
            age = user_data['age']
            if 'below 18' in eligibility_text and age < 18:
                matches.append('Age criteria met (below 18)')
            elif 'above 60' in eligibility_text and age > 60:
                matches.append('Age criteria met (senior citizen)')
            elif 'between' in eligibility_text:
                # Try to extract age range
                import re
                age_range = re.findall(r'between (\d+) and (\d+)', eligibility_text)
                if age_range:
                    min_age, max_age = int(age_range[0][0]), int(age_range[0][1])
                    if min_age <= age <= max_age:
                        matches.append(f'Age criteria met ({min_age}-{max_age} years)')
        
        # Gender-based matching
        if 'gender' in user_data:
            gender = user_data['gender'].lower()
            if gender in eligibility_text:
                matches.append(f'Gender criteria met ({gender})')
        
        # Income-based matching
        if 'income' in user_data:
            income = user_data['income']
            if 'below poverty line' in eligibility_text or 'bpl' in eligibility_text:
                # Assume BPL if income < 100000
                if income < 100000:
                    matches.append('Income criteria met (BPL)')
            elif 'low income' in eligibility_text and income < 300000:
                matches.append('Income criteria met (low income)')
        
        # State-based matching
        if 'state' in user_data and self.state:
            if user_data['state'].lower() in self.state.lower():
                matches.append(f'State criteria met ({self.state})')
        
        # Category-based matching (SC/ST/OBC)
        if 'category' in user_data:
            category = user_data['category'].lower()
            if category in eligibility_text:
                matches.append(f'Category criteria met ({category})')
        
        # Occupation-based matching
        if 'occupation' in user_data:
            occupation = user_data['occupation'].lower()
            if occupation in eligibility_text:
                matches.append(f'Occupation criteria met ({occupation})')
        
        # If no specific matches but general keywords found
        if not matches:
            general_keywords = ['citizen', 'resident', 'indian', 'all', 'eligible']
            if any(keyword in eligibility_text for keyword in general_keywords):
                matches.append('General eligibility criteria may apply')
        
        eligible = len(matches) > 0
        confidence = min(len(matches) * 0.3, 1.0)  # Max 1.0 confidence
        
        return {
            'eligible': eligible,
            'confidence': confidence,
            'matches': matches,
            'eligibility_text': self.eligibility
        }


class SchemeDocument(models.Model):
    """Individual documents required for a scheme"""
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='required_documents')
    document_name = models.CharField(max_length=200)
    document_type = models.CharField(
        max_length=50,
        choices=[
            ('identity', 'Identity Proof'),
            ('address', 'Address Proof'),
            ('income', 'Income Proof'),
            ('age', 'Age Proof'),
            ('education', 'Education Certificate'),
            ('employment', 'Employment Proof'),
            ('medical', 'Medical Certificate'),
            ('other', 'Other'),
        ],
        default='other'
    )
    is_mandatory = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['scheme', 'document_name']
    
    def __str__(self):
        return f"{self.scheme.scheme_name} - {self.document_name}"
