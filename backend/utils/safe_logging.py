"""
Utility functions for safe logging that mask sensitive information.
"""
import re
from typing import Any, Optional


def mask_phone_number(phone: str) -> str:
    """
    Mask phone number showing only last 4 digits.
    Example: +919876543210 -> +91******3210
    """
    if not phone or len(phone) < 4:
        return "****"
    
    # Remove any non-digit characters except +
    clean_phone = re.sub(r'[^\d+]', '', phone)
    
    if len(clean_phone) <= 4:
        return "****"
    
    # Show country code if present and last 4 digits
    if clean_phone.startswith('+'):
        if len(clean_phone) <= 7:  # +XX and 4 digits
            return clean_phone[:3] + "****"
        return clean_phone[:3] + "*" * (len(clean_phone) - 7) + clean_phone[-4:]
    else:
        return "*" * (len(clean_phone) - 4) + clean_phone[-4:]


def mask_email(email: str) -> str:
    """
    Mask email showing only first 2 chars and domain.
    Example: john.doe@example.com -> jo****@example.com
    """
    if not email or '@' not in email:
        return "****@****.***"
    
    local, domain = email.split('@', 1)
    
    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = local[:2] + "*" * (len(local) - 2)
    
    return f"{masked_local}@{domain}"


def mask_aadhaar(aadhaar: str) -> str:
    """
    Mask Aadhaar number showing only last 4 digits.
    Example: 123456789012 -> ********9012
    """
    if not aadhaar:
        return "****"
    
    # Remove any non-digit characters
    clean_aadhaar = re.sub(r'\D', '', aadhaar)
    
    if len(clean_aadhaar) <= 4:
        return "****"
    
    return "*" * (len(clean_aadhaar) - 4) + clean_aadhaar[-4:]


def mask_name(name: str) -> str:
    """
    Mask name showing only first name initial and last name initial.
    Example: John Doe Smith -> J*** D*** S****
    """
    if not name:
        return "****"
    
    parts = name.split()
    masked_parts = []
    
    for part in parts:
        if len(part) <= 1:
            masked_parts.append("*")
        else:
            masked_parts.append(part[0] + "*" * (len(part) - 1))
    
    return " ".join(masked_parts)


def mask_address(address: str) -> str:
    """
    Mask address showing only first few characters.
    Example: 123 Main Street, City -> 123 M*** S*****, C***
    """
    if not address:
        return "****"
    
    if len(address) <= 10:
        return "*" * len(address)
    
    # Show first 6 characters and mask the rest
    return address[:6] + "*" * (len(address) - 6)


def safe_log_user_action(action: str, phone: Optional[str] = None, 
                        email: Optional[str] = None, user_id: Optional[str] = None) -> str:
    """
    Create a safe log message for user actions with masked sensitive data.
    """
    parts = [action]
    
    if user_id:
        parts.append(f"user_id: {user_id}")
    
    if phone:
        parts.append(f"phone: {mask_phone_number(phone)}")
    
    if email:
        parts.append(f"email: {mask_email(email)}")
    
    return " | ".join(parts)


def safe_log_profile_data(profile_data: dict) -> dict:
    """
    Create a safe version of profile data for logging with masked sensitive fields.
    """
    safe_data = profile_data.copy()
    
    # Mask sensitive fields
    if 'phone_number' in safe_data:
        safe_data['phone_number'] = mask_phone_number(safe_data['phone_number'])
    
    if 'email' in safe_data:
        safe_data['email'] = mask_email(safe_data['email'])
    
    if 'aadhaar_number' in safe_data:
        safe_data['aadhaar_number'] = mask_aadhaar(safe_data['aadhaar_number'])
    
    if 'name' in safe_data:
        safe_data['name'] = mask_name(safe_data['name'])
    
    if 'address' in safe_data:
        safe_data['address'] = mask_address(safe_data['address'])
    
    return safe_data