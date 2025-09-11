import csv
import json
import re
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from schemes.models import Scheme, SchemeCategory, SchemeLevel


class Command(BaseCommand):
    help = 'Import government schemes from CSV or JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the CSV or JSON file containing schemes data'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['csv', 'json'],
            help='File format (auto-detected if not specified)'
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing schemes with same name'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview import without saving to database'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        file_format = options.get('format')
        overwrite = options['overwrite']
        dry_run = options['dry_run']

        # Auto-detect format if not specified
        if not file_format:
            if file_path.endswith('.csv'):
                file_format = 'csv'
            elif file_path.endswith('.json'):
                file_format = 'json'
            else:
                raise CommandError('Cannot detect file format. Please specify --format')

        try:
            if file_format == 'csv':
                schemes_data = self.read_csv(file_path)
            else:
                schemes_data = self.read_json(file_path)

            self.stdout.write(f"Found {len(schemes_data)} schemes to import")

            if dry_run:
                self.preview_import(schemes_data)
                return

            imported_count = self.import_schemes(schemes_data, overwrite)
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {imported_count} schemes')
            )

        except Exception as e:
            raise CommandError(f'Error importing schemes: {str(e)}')

    def read_csv(self, file_path):
        """Read schemes from CSV file"""
        schemes = []
        
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Clean and map CSV columns to model fields
                scheme_data = self.clean_scheme_data({
                    'scheme_name': row.get('Scheme Name') or row.get('scheme_name', ''),
                    'details': row.get('Details') or row.get('description', ''),
                    'benefits': row.get('Benefits') or row.get('benefits', ''),
                    'eligibility': row.get('Eligibility') or row.get('eligibility', ''),
                    'application': row.get('Application Process') or row.get('application', ''),
                    'documents': row.get('Documents Required') or row.get('documents', ''),
                    'level': row.get('Level') or row.get('government_level', 'central'),
                    'scheme_category': row.get('Category') or row.get('category', 'other'),
                    'state': row.get('State') or row.get('state', ''),
                    'ministry_department': row.get('Ministry') or row.get('ministry', ''),
                    'website_url': row.get('Website') or row.get('url', ''),
                })
                
                if scheme_data['scheme_name']:  # Only add if scheme has a name
                    schemes.append(scheme_data)
        
        return schemes

    def read_json(self, file_path):
        """Read schemes from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
        
        schemes = []
        
        # Handle different JSON structures
        if isinstance(data, list):
            schemes_list = data
        elif isinstance(data, dict) and 'schemes' in data:
            schemes_list = data['schemes']
        else:
            raise CommandError('Invalid JSON structure. Expected list or object with "schemes" key')
        
        for item in schemes_list:
            scheme_data = self.clean_scheme_data(item)
            if scheme_data['scheme_name']:
                schemes.append(scheme_data)
        
        return schemes

    def clean_scheme_data(self, raw_data):
        """Clean and validate scheme data"""
        cleaned = {}
        
        # Clean scheme name
        scheme_name = str(raw_data.get('scheme_name', '')).strip()
        cleaned['scheme_name'] = self.clean_text(scheme_name)
        
        # Clean text fields
        text_fields = ['details', 'benefits', 'eligibility', 'application', 'documents']
        for field in text_fields:
            value = raw_data.get(field, '')
            cleaned[field] = self.clean_text(str(value)) if value else ''
        
        # Clean and validate level
        level = str(raw_data.get('level', 'central')).lower().strip()
        level_mapping = {
            'central': 'central',
            'state': 'state',
            'district': 'district',
            'block': 'block',
            'panchayat': 'panchayat',
            'national': 'central',
            'federal': 'central',
            'local': 'district'
        }
        cleaned['level'] = level_mapping.get(level, 'central')
        
        # Clean and validate category
        category = str(raw_data.get('scheme_category', 'other')).lower().strip()
        category_mapping = {
            'agriculture': 'agriculture',
            'farming': 'agriculture',
            'education': 'education',
            'learning': 'education',
            'health': 'healthcare',
            'healthcare': 'healthcare',
            'medical': 'healthcare',
            'employment': 'employment',
            'job': 'employment',
            'work': 'employment',
            'women': 'women_child',
            'child': 'women_child',
            'rural': 'rural_development',
            'housing': 'housing',
            'financial': 'financial_inclusion',
            'disability': 'disability',
            'elderly': 'elderly',
            'minority': 'minority',
            'tribal': 'tribal',
            'skill': 'skill_development',
            'environment': 'environment',
            'transport': 'transport',
            'social': 'social_welfare',
        }
        
        # Find best category match
        cleaned['scheme_category'] = 'other'
        for keyword, cat in category_mapping.items():
            if keyword in category:
                cleaned['scheme_category'] = cat
                break
        
        # Clean other fields
        cleaned['state'] = self.clean_text(str(raw_data.get('state', '')))
        cleaned['ministry_department'] = self.clean_text(str(raw_data.get('ministry_department', '')))
        
        # Clean URL
        website_url = str(raw_data.get('website_url', '')).strip()
        if website_url and not website_url.startswith(('http://', 'https://')):
            website_url = 'https://' + website_url
        cleaned['website_url'] = website_url if self.is_valid_url(website_url) else ''
        
        return cleaned

    def clean_text(self, text):
        """Clean text content"""
        if not text or text.lower() in ['null', 'none', 'n/a', 'na', '-']:
            return ''
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove HTML tags if any
        text = re.sub(r'<[^>]+>', '', text)
        
        # Fix common encoding issues
        text = text.replace('â€™', "'").replace('â€œ', '"').replace('â€�', '"')
        
        return text

    def is_valid_url(self, url):
        """Basic URL validation"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None

    def preview_import(self, schemes_data):
        """Preview what will be imported"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write("IMPORT PREVIEW (DRY RUN)")
        self.stdout.write("="*50)
        
        categories = {}
        levels = {}
        
        for i, scheme in enumerate(schemes_data[:10]):  # Show first 10
            self.stdout.write(f"\n{i+1}. {scheme['scheme_name']}")
            self.stdout.write(f"   Level: {scheme['level']}")
            self.stdout.write(f"   Category: {scheme['scheme_category']}")
            self.stdout.write(f"   State: {scheme['state'] or 'N/A'}")
            
            # Count categories and levels
            categories[scheme['scheme_category']] = categories.get(scheme['scheme_category'], 0) + 1
            levels[scheme['level']] = levels.get(scheme['level'], 0) + 1
        
        if len(schemes_data) > 10:
            self.stdout.write(f"\n... and {len(schemes_data) - 10} more schemes")
        
        self.stdout.write(f"\nSummary:")
        self.stdout.write(f"Categories: {dict(categories)}")
        self.stdout.write(f"Levels: {dict(levels)}")

    def import_schemes(self, schemes_data, overwrite=False):
        """Import schemes into database"""
        imported_count = 0
        
        for scheme_data in schemes_data:
            try:
                # Check if scheme exists
                existing_scheme = None
                try:
                    existing_scheme = Scheme.objects.get(scheme_name=scheme_data['scheme_name'])
                except Scheme.DoesNotExist:
                    pass
                
                if existing_scheme:
                    if overwrite:
                        # Update existing scheme
                        for field, value in scheme_data.items():
                            if value:  # Only update non-empty values
                                setattr(existing_scheme, field, value)
                        existing_scheme.save()
                        self.stdout.write(f"Updated: {scheme_data['scheme_name']}")
                        imported_count += 1
                    else:
                        self.stdout.write(f"Skipped (exists): {scheme_data['scheme_name']}")
                else:
                    # Create new scheme
                    scheme = Scheme.objects.create(**scheme_data)
                    self.stdout.write(f"Created: {scheme.scheme_name}")
                    imported_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error importing {scheme_data['scheme_name']}: {str(e)}")
                )
        
        return imported_count
