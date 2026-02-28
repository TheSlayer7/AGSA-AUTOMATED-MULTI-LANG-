#!/usr/bin/env python
"""
High-Performance CSV Upload System for Government Schemes
Features:
- Batch processing with configurable batch sizes
- Conflict management (insert/update/skip strategies)
- Minimal database operations with bulk operations
- Progress tracking and detailed logging
- Memory-efficient streaming for large files
- Transaction safety with rollback capability
- Duplicate detection and handling
- Data validation and cleaning
"""

import csv
import logging
import time
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from schemes.models import Scheme, SchemeCategory, SchemeLevel


@dataclass
class ImportStats:
    """Statistics for import operation"""
    total_rows: int = 0
    processed_rows: int = 0
    created_schemes: int = 0
    updated_schemes: int = 0
    skipped_schemes: int = 0
    error_schemes: int = 0
    batch_count: int = 0
    start_time: float = 0
    end_time: float = 0
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time
    
    @property
    def rows_per_second(self) -> float:
        return self.processed_rows / self.duration if self.duration > 0 else 0


class OptimizedCSVUploader:
    """High-performance CSV uploader with batch processing and conflict management"""
    
    def __init__(self, batch_size: int = 1000, conflict_strategy: str = 'skip'):
        self.batch_size = batch_size
        self.conflict_strategy = conflict_strategy  # 'skip', 'update', 'replace'
        self.stats = ImportStats()
        self.logger = self._setup_logger()
        
        # Cache for existing schemes to minimize DB queries
        self._existing_schemes_cache = {}
        self._refresh_cache()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup detailed logging"""
        logger = logging.getLogger('csv_uploader')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _refresh_cache(self):
        """Refresh cache of existing schemes"""
        self.logger.info("Refreshing existing schemes cache...")
        
        # Use values_list for memory efficiency
        existing_schemes = Scheme.objects.values_list(
            'scheme_name', 'id', 'slug', 'scheme_category'
        )
        
        self._existing_schemes_cache = {
            name.lower().strip(): {
                'id': scheme_id, 
                'slug': slug, 
                'category': category
            }
            for name, scheme_id, slug, category in existing_schemes
        }
        
        self.logger.info(f"Cached {len(self._existing_schemes_cache)} existing schemes")
    
    def upload_csv(self, file_path: str, dry_run: bool = False) -> ImportStats:
        """Main upload method with full optimization"""
        self.stats.start_time = time.time()
        self.logger.info(f"Starting CSV upload: {file_path}")
        self.logger.info(f"Batch size: {self.batch_size}, Strategy: {self.conflict_strategy}")
        
        try:
            with self._count_csv_rows(file_path) as total_rows:
                self.stats.total_rows = total_rows
                self.logger.info(f"Total rows to process: {total_rows}")
            
            if dry_run:
                return self._dry_run_analysis(file_path)
            
            return self._process_csv_batches(file_path)
            
        except Exception as e:
            self.logger.error(f"Upload failed: {str(e)}")
            raise
        finally:
            self.stats.end_time = time.time()
            self._log_final_stats()
    
    @contextmanager
    def _count_csv_rows(self, file_path: str):
        """Efficiently count CSV rows"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            # Skip header
            next(f)
            row_count = sum(1 for _ in f)
            yield row_count
    
    def _process_csv_batches(self, file_path: str) -> ImportStats:
        """Process CSV in optimized batches"""
        batch_buffer = []
        batch_num = 0
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    cleaned_data = self._clean_and_validate_row(row, row_num)
                    if cleaned_data:
                        batch_buffer.append(cleaned_data)
                    
                    # Process batch when full
                    if len(batch_buffer) >= self.batch_size:
                        batch_num += 1
                        self._process_batch(batch_buffer, batch_num)
                        batch_buffer = []
                        
                        # Log progress
                        if batch_num % 10 == 0:
                            self._log_progress()
                
                except Exception as e:
                    self.logger.error(f"Error processing row {row_num}: {str(e)}")
                    self.stats.error_schemes += 1
            
            # Process remaining rows
            if batch_buffer:
                batch_num += 1
                self._process_batch(batch_buffer, batch_num)
        
        self.stats.batch_count = batch_num
        return self.stats
    
    def _clean_and_validate_row(self, row: Dict[str, Any], row_num: int) -> Optional[Dict[str, Any]]:
        """Clean and validate a single row"""
        try:
            # Map CSV columns to model fields with multiple possible column names
            field_mappings = {
                'scheme_name': ['scheme_name', 'Scheme Name', 'name', 'title'],
                'details': ['details', 'Details', 'description', 'summary'],
                'benefits': ['benefits', 'Benefits', 'benefit', 'advantages'],
                'eligibility': ['eligibility', 'Eligibility', 'criteria', 'eligible'],
                'application': ['application', 'Application Process', 'process', 'how_to_apply'],
                'documents': ['documents', 'Documents Required', 'required_documents'],
                'level': ['level', 'Level', 'government_level', 'govt_level'],
                'scheme_category': ['schemeCategory', 'Category', 'category', 'scheme_category', 'type'],
                'state': ['state', 'State', 'region'],
                'ministry_department': ['ministry_department', 'Ministry', 'ministry', 'department'],
                'website_url': ['website_url', 'Website', 'url', 'link'],
            }
            
            cleaned = {}
            
            # Extract and clean each field
            for field, possible_columns in field_mappings.items():
                value = None
                for col in possible_columns:
                    if col in row and row[col]:
                        value = str(row[col]).strip()
                        break
                
                if field == 'scheme_name':
                    if not value:
                        return None  # Skip rows without scheme name
                    cleaned[field] = self._clean_text(value)
                elif field == 'scheme_category':
                    cleaned[field] = self._normalize_category(value or 'other')
                elif field == 'level':
                    cleaned[field] = self._normalize_level(value or 'central')
                elif field == 'website_url':
                    cleaned[field] = self._clean_url(value or '')
                else:
                    cleaned[field] = self._clean_text(value or '')
            
            # Generate slug
            cleaned['slug'] = slugify(cleaned['scheme_name'])
            
            # Set defaults
            cleaned['is_active'] = True
            
            return cleaned
            
        except Exception as e:
            self.logger.error(f"Row {row_num} validation failed: {str(e)}")
            return None
    
    def _process_batch(self, batch_data: List[Dict[str, Any]], batch_num: int):
        """Process a batch with optimized database operations"""
        self.logger.info(f"Processing batch {batch_num} ({len(batch_data)} items)")
        
        # Separate into create/update operations
        to_create = []
        to_update = []
        to_skip = []
        
        for item in batch_data:
            scheme_name_key = item['scheme_name'].lower().strip()
            
            if scheme_name_key in self._existing_schemes_cache:
                if self.conflict_strategy == 'skip':
                    to_skip.append(item)
                elif self.conflict_strategy in ['update', 'replace']:
                    item['existing_id'] = self._existing_schemes_cache[scheme_name_key]['id']
                    to_update.append(item)
            else:
                to_create.append(item)
        
        # Execute batch operations with transactions
        with transaction.atomic():
            created_count = self._bulk_create_schemes(to_create)
            updated_count = self._bulk_update_schemes(to_update)
            skipped_count = len(to_skip)
        
        # Update statistics
        self.stats.created_schemes += created_count
        self.stats.updated_schemes += updated_count
        self.stats.skipped_schemes += skipped_count
        self.stats.processed_rows += len(batch_data)
        
        # Update cache for newly created schemes
        if to_create:
            self._update_cache_with_new_schemes(to_create)
        
        self.logger.info(
            f"Batch {batch_num} complete: "
            f"{created_count} created, {updated_count} updated, {skipped_count} skipped"
        )
    
    def _bulk_create_schemes(self, to_create: List[Dict[str, Any]]) -> int:
        """Bulk create schemes for maximum performance"""
        if not to_create:
            return 0
        
        schemes_to_create = [
            Scheme(**self._prepare_scheme_data(item))
            for item in to_create
        ]
        
        try:
            Scheme.objects.bulk_create(
                schemes_to_create,
                batch_size=500,  # Split large batches for memory efficiency
                ignore_conflicts=True  # Handle any race conditions
            )
            return len(schemes_to_create)
        except Exception as e:
            self.logger.error(f"Bulk create failed: {str(e)}")
            # Fallback to individual creates
            return self._fallback_individual_creates(to_create)
    
    def _bulk_update_schemes(self, to_update: List[Dict[str, Any]]) -> int:
        """Bulk update schemes efficiently"""
        if not to_update:
            return 0
        
        updated_count = 0
        
        # Group updates by ID for efficiency
        updates_by_id = {item['existing_id']: item for item in to_update}
        
        # Fetch existing schemes to update
        existing_schemes = Scheme.objects.filter(
            id__in=updates_by_id.keys()
        ).select_for_update()
        
        schemes_to_update = []
        
        for scheme in existing_schemes:
            update_data = updates_by_id[scheme.id]
            
            # Update fields based on strategy
            if self.conflict_strategy == 'replace':
                # Replace all fields
                for field, value in self._prepare_scheme_data(update_data).items():
                    setattr(scheme, field, value)
            else:  # update strategy
                # Only update non-empty fields
                for field, value in self._prepare_scheme_data(update_data).items():
                    if value and value.strip():
                        setattr(scheme, field, value)
            
            schemes_to_update.append(scheme)
        
        if schemes_to_update:
            try:
                # Use bulk_update for efficiency
                fields_to_update = [
                    'scheme_name', 'details', 'benefits', 'eligibility',
                    'application', 'documents', 'level', 'scheme_category',
                    'state', 'ministry_department', 'website_url', 'slug'
                ]
                
                Scheme.objects.bulk_update(
                    schemes_to_update,
                    fields_to_update,
                    batch_size=500
                )
                updated_count = len(schemes_to_update)
            except Exception as e:
                self.logger.error(f"Bulk update failed: {str(e)}")
                # Fallback to individual updates
                updated_count = self._fallback_individual_updates(schemes_to_update)
        
        return updated_count
    
    def _prepare_scheme_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for scheme creation/update"""
        # Remove helper fields
        data = item.copy()
        data.pop('existing_id', None)
        return data
    
    def _fallback_individual_creates(self, to_create: List[Dict[str, Any]]) -> int:
        """Fallback to individual creates if bulk fails"""
        created_count = 0
        for item in to_create:
            try:
                Scheme.objects.create(**self._prepare_scheme_data(item))
                created_count += 1
            except Exception as e:
                self.logger.error(f"Individual create failed for {item['scheme_name']}: {str(e)}")
        return created_count
    
    def _fallback_individual_updates(self, schemes: List[Scheme]) -> int:
        """Fallback to individual updates if bulk fails"""
        updated_count = 0
        for scheme in schemes:
            try:
                scheme.save()
                updated_count += 1
            except Exception as e:
                self.logger.error(f"Individual update failed for {scheme.scheme_name}: {str(e)}")
        return updated_count
    
    def _update_cache_with_new_schemes(self, created_schemes: List[Dict[str, Any]]):
        """Update cache with newly created schemes"""
        # This is a simplified update - in production you might want to refetch from DB
        for scheme_data in created_schemes:
            name_key = scheme_data['scheme_name'].lower().strip()
            self._existing_schemes_cache[name_key] = {
                'id': None,  # We don't have the ID yet
                'slug': scheme_data['slug'],
                'category': scheme_data['scheme_category']
            }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text or text.lower() in ['null', 'none', 'n/a', 'na', '-', '']:
            return ''
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove HTML tags
        import re
        text = re.sub(r'<[^>]+>', '', text)
        
        # Fix encoding issues
        text = text.replace('â€™', "'").replace('â€œ', '"').replace('â€�', '"')
        
        return text.strip()
    
    def _normalize_category(self, category: str) -> str:
        """Normalize category to valid enum value"""
        if not category:
            return SchemeCategory.OTHER
        
        category_lower = category.lower().strip()
        
        # Mapping from common terms to SchemeCategory values
        mappings = {
            'agriculture': SchemeCategory.AGRICULTURE,
            'farming': SchemeCategory.AGRICULTURE,
            'crop': SchemeCategory.AGRICULTURE,
            'education': SchemeCategory.EDUCATION,
            'school': SchemeCategory.EDUCATION,
            'scholarship': SchemeCategory.EDUCATION,
            'health': SchemeCategory.HEALTHCARE,
            'healthcare': SchemeCategory.HEALTHCARE,
            'medical': SchemeCategory.HEALTHCARE,
            'employment': SchemeCategory.EMPLOYMENT,
            'job': SchemeCategory.EMPLOYMENT,
            'work': SchemeCategory.EMPLOYMENT,
            'women': SchemeCategory.WOMEN_CHILD,
            'child': SchemeCategory.WOMEN_CHILD,
            'rural': SchemeCategory.RURAL_DEVELOPMENT,
            'housing': SchemeCategory.HOUSING,
            'financial': SchemeCategory.FINANCIAL_INCLUSION,
            'loan': SchemeCategory.FINANCIAL_INCLUSION,
            'disability': SchemeCategory.DISABILITY,
            'elderly': SchemeCategory.ELDERLY,
            'minority': SchemeCategory.MINORITY,
            'tribal': SchemeCategory.TRIBAL,
            'skill': SchemeCategory.SKILL_DEVELOPMENT,
            'training': SchemeCategory.SKILL_DEVELOPMENT,
            'environment': SchemeCategory.ENVIRONMENT,
            'transport': SchemeCategory.TRANSPORT,
            'social': SchemeCategory.SOCIAL_WELFARE,
        }
        
        # Find best match
        for keyword, enum_value in mappings.items():
            if keyword in category_lower:
                return enum_value
        
        return SchemeCategory.OTHER
    
    def _normalize_level(self, level: str) -> str:
        """Normalize government level to valid enum value"""
        if not level:
            return SchemeLevel.CENTRAL
        
        level_lower = level.lower().strip()
        
        mappings = {
            'central': SchemeLevel.CENTRAL,
            'state': SchemeLevel.STATE,
            'district': SchemeLevel.DISTRICT,
            'block': SchemeLevel.BLOCK,
            'panchayat': SchemeLevel.PANCHAYAT,
        }
        
        for keyword, enum_value in mappings.items():
            if keyword in level_lower:
                return enum_value
        
        return SchemeLevel.CENTRAL
    
    def _clean_url(self, url: str) -> str:
        """Clean and validate URL"""
        if not url:
            return ''
        
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Basic URL validation
        import re
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        
        return url if url_pattern.match(url) else ''
    
    def _dry_run_analysis(self, file_path: str) -> ImportStats:
        """Perform dry run analysis"""
        self.logger.info("Performing dry run analysis...")
        
        sample_size = min(1000, self.stats.total_rows)
        categories = defaultdict(int)
        levels = defaultdict(int)
        conflicts = 0
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for i, row in enumerate(reader):
                if i >= sample_size:
                    break
                
                cleaned = self._clean_and_validate_row(row, i + 1)
                if cleaned:
                    categories[cleaned['scheme_category']] += 1
                    levels[cleaned['level']] += 1
                    
                    # Check for conflicts
                    name_key = cleaned['scheme_name'].lower().strip()
                    if name_key in self._existing_schemes_cache:
                        conflicts += 1
        
        # Log analysis
        self.logger.info(f"\nDRY RUN ANALYSIS (sample of {sample_size} rows):")
        self.logger.info(f"Categories: {dict(categories)}")
        self.logger.info(f"Levels: {dict(levels)}")
        self.logger.info(f"Potential conflicts: {conflicts}")
        
        return self.stats
    
    def _log_progress(self):
        """Log current progress"""
        elapsed = time.time() - self.stats.start_time
        progress_pct = (self.stats.processed_rows / self.stats.total_rows * 100) if self.stats.total_rows > 0 else 0
        rate = self.stats.processed_rows / elapsed if elapsed > 0 else 0
        
        self.logger.info(
            f"Progress: {self.stats.processed_rows}/{self.stats.total_rows} "
            f"({progress_pct:.1f}%) - {rate:.1f} rows/sec"
        )
    
    def _log_final_stats(self):
        """Log final import statistics"""
        self.logger.info("\n" + "="*60)
        self.logger.info("IMPORT COMPLETED")
        self.logger.info("="*60)
        self.logger.info(f"Total rows processed: {self.stats.processed_rows:,}")
        self.logger.info(f"Schemes created: {self.stats.created_schemes:,}")
        self.logger.info(f"Schemes updated: {self.stats.updated_schemes:,}")
        self.logger.info(f"Schemes skipped: {self.stats.skipped_schemes:,}")
        self.logger.info(f"Errors: {self.stats.error_schemes:,}")
        self.logger.info(f"Batches processed: {self.stats.batch_count}")
        self.logger.info(f"Duration: {self.stats.duration:.2f} seconds")
        self.logger.info(f"Processing rate: {self.stats.rows_per_second:.1f} rows/second")
        self.logger.info("="*60)


class Command(BaseCommand):
    """Django management command for optimized CSV upload"""
    
    help = 'High-performance CSV upload with batch processing and conflict management'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the CSV file'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Batch size for processing (default: 1000)'
        )
        parser.add_argument(
            '--conflict-strategy',
            choices=['skip', 'update', 'replace'],
            default='skip',
            help='How to handle existing schemes (default: skip)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Analyze file without importing'
        )
    
    def handle(self, *args, **options):
        file_path = options['file_path']
        batch_size = options['batch_size']
        conflict_strategy = options['conflict_strategy']
        dry_run = options['dry_run']
        
        uploader = OptimizedCSVUploader(
            batch_size=batch_size,
            conflict_strategy=conflict_strategy
        )
        
        try:
            stats = uploader.upload_csv(file_path, dry_run=dry_run)
            
            if not dry_run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully processed {stats.processed_rows:,} rows '
                        f'({stats.created_schemes:,} created, {stats.updated_schemes:,} updated)'
                    )
                )
            
        except Exception as e:
            raise CommandError(f'Upload failed: {str(e)}')
