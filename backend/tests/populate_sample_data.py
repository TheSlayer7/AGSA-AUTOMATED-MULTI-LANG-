#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.safe_logging import mask_phone_number

"""
Script to populate the database with sample DigiLocker data.

This script creates sample users, document types, and documents
to demonstrate the dynamic document management system.
"""

import os
import sys
import django
from datetime import date, datetime, timedelta
from django.utils import timezone

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agsa.settings')
django.setup()

from api.models import UserProfile, DocumentType, Document, Session, OTPRequest


def create_sample_data():
    """Create sample data for DigiLocker mock system."""
    
    print("Creating sample document types...")
    
    # Create document types
    doc_types = [
        {"name": "Aadhaar Card", "issued_by": "UIDAI", "category": "identity"},
        {"name": "PAN Card", "issued_by": "Income Tax Department", "category": "identity"},
        {"name": "Driving License", "issued_by": "Transport Department", "category": "license"},
        {"name": "Voter ID", "issued_by": "Election Commission", "category": "identity"},
        {"name": "Passport", "issued_by": "Ministry of External Affairs", "category": "identity"},
        {"name": "Vehicle RC", "issued_by": "Transport Department", "category": "vehicle"},
        {"name": "Property Tax Receipt", "issued_by": "Municipal Corporation", "category": "tax"},
        {"name": "Electricity Bill", "issued_by": "State Electricity Board", "category": "utility"},
        {"name": "Gas Connection", "issued_by": "Gas Distribution Company", "category": "utility"},
        {"name": "Bank Statement", "issued_by": "State Bank of India", "category": "financial"},
    ]
    
    created_types = []
    for doc_type_data in doc_types:
        doc_type, created = DocumentType.objects.get_or_create(
            name=doc_type_data["name"],
            defaults=doc_type_data
        )
        created_types.append(doc_type)
        print(f"  {'Created' if created else 'Found'}: {doc_type.name}")
    
    print("\nCreating sample user profiles...")
    
    # Create user profiles
    users_data = [
        {
            "name": "Rajesh Kumar",
            "dob": date(1985, 6, 15),
            "gender": "M",
            "address": "123 MG Road, Bangalore, Karnataka 560001",
            "phone_number": "+919876543210",
            "email": "rajesh.kumar@email.com",
            "aadhaar_number": "****-****-1234"
        },
        {
            "name": "Priya Sharma",
            "dob": date(1990, 8, 22),
            "gender": "F",
            "address": "456 Connaught Place, New Delhi 110001",
            "phone_number": "+919876543211",
            "email": "priya.sharma@email.com",
            "aadhaar_number": "****-****-5678"
        },
        {
            "name": "Amit Patel",
            "dob": date(1982, 3, 10),
            "gender": "M",
            "address": "789 Marine Drive, Mumbai, Maharashtra 400001",
            "phone_number": "+919876543212",
            "email": "amit.patel@email.com",
            "aadhaar_number": "****-****-9012"
        },
        {
            "name": "Sunita Verma",
            "dob": date(1988, 12, 5),
            "gender": "F",
            "address": "321 Park Street, Kolkata, West Bengal 700001",
            "phone_number": "+919876543213",
            "email": "sunita.verma@email.com",
            "aadhaar_number": "****-****-3456"
        }
    ]
    
    created_users = []
    for user_data in users_data:
        user_profile, created = UserProfile.objects.get_or_create(
            phone_number=user_data["phone_number"],
            defaults=user_data
        )
        created_users.append(user_profile)
        print(f"  {'Created' if created else 'Found'}: {user_profile.name}")
    
    print("\nCreating sample sessions...")
    
    # Create sample sessions
    for user in created_users[:2]:  # Create sessions for first 2 users
        session, created = Session.objects.get_or_create(
            user_profile=user,
            defaults={
                'is_authenticated': True,
                'expires_at': timezone.now() + timedelta(hours=24)
            }
        )
        print(f"  {'Created' if created else 'Found'} session for: {user.name}")
    
    print("\nCreating sample OTP requests...")
    
    # Create sample OTP requests
    for user in created_users:
        otp, created = OTPRequest.objects.get_or_create(
            phone_number=user.phone_number,
            defaults={
                'otp_code': '123456',
                'is_verified': True,
                'expires_at': timezone.now() + timedelta(minutes=10)
            }
        )
        print(f"  {'Created' if created else 'Found'} OTP for: {mask_phone_number(user.phone_number)}")
    
    print("\n✅ Sample data created successfully!")
    print(f"📊 Created {len(created_types)} document types")
    print(f"👥 Created {len(created_users)} user profiles")
    print(f"🔐 Created sessions and OTP requests")
    
    print("\n📝 Next steps:")
    print("1. Start the Django server: uv run python manage.py runserver")
    print("2. Visit admin panel: http://localhost:8000/admin/")
    print("3. Login with: admin / (the password you set)")
    print("4. Upload documents via the admin interface")
    print("5. Test API endpoints with the uploaded documents")


if __name__ == '__main__':
    create_sample_data()
