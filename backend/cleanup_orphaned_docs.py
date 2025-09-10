#!/usr/bin/env python3
"""
Script to check and clean up orphaned document records
"""
import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.dirname(__file__))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agsa.settings')
django.setup()

from api.models import Document

def check_orphaned_documents():
    """Check for documents with missing files."""
    print("🔍 Checking for orphaned document records...")
    
    orphaned_docs = []
    all_documents = Document.objects.all()
    
    print(f"📊 Total documents in database: {all_documents.count()}")
    
    for doc in all_documents:
        if doc.document_file:
            try:
                # Try to access the file
                _ = doc.document_file.size
                print(f"✅ {doc.doc_id}: {doc.document_file.name} - OK")
            except (FileNotFoundError, OSError):
                print(f"❌ {doc.doc_id}: {doc.document_file.name} - FILE NOT FOUND")
                orphaned_docs.append(doc)
        else:
            print(f"⚠️  {doc.doc_id}: No file attached")
            orphaned_docs.append(doc)
    
    print(f"\n🚨 Found {len(orphaned_docs)} orphaned document(s)")
    
    if orphaned_docs:
        print("\nOrphaned documents:")
        for doc in orphaned_docs:
            print(f"  - {doc.doc_id}: {doc.document_type.name} (User: {doc.user_profile.name})")
            print(f"    File path: {doc.document_file.name if doc.document_file else 'None'}")
    
    return orphaned_docs

def cleanup_orphaned_documents(orphaned_docs):
    """Clean up orphaned documents."""
    if not orphaned_docs:
        print("✅ No orphaned documents to clean up")
        return
    
    print(f"\n🧹 Cleaning up {len(orphaned_docs)} orphaned document(s)...")
    
    for doc in orphaned_docs:
        print(f"🗑️  Deleting: {doc.doc_id} - {doc.document_type.name}")
        doc.delete()
    
    print("✅ Cleanup complete!")

if __name__ == "__main__":
    orphaned = check_orphaned_documents()
    
    if orphaned:
        response = input(f"\n❓ Delete {len(orphaned)} orphaned document(s)? (y/N): ")
        if response.lower() == 'y':
            cleanup_orphaned_documents(orphaned)
        else:
            print("❌ Cleanup cancelled")
    else:
        print("✅ No cleanup needed!")
