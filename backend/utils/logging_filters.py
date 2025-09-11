"""
Custom logging filters for security and privacy protection.
"""
import logging
import re
from typing import List, Pattern


class SensitiveDataFilter(logging.Filter):
    """
    Logging filter that removes or masks sensitive information from log records.
    """
    
    # Patterns for detecting sensitive information
    SENSITIVE_PATTERNS: List[Pattern] = [
        re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),  # Aadhaar pattern
        re.compile(r'\b[789]\d{9}\b'),                    # Indian phone number
        re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),  # Email
        re.compile(r'\bpassword\s*[:=]\s*[^\s]+', re.IGNORECASE),
        re.compile(r'\btoken\s*[:=]\s*[^\s]+', re.IGNORECASE),
        re.compile(r'\bapi_key\s*[:=]\s*[^\s]+', re.IGNORECASE),
        re.compile(r'\bsecret\s*[:=]\s*[^\s]+', re.IGNORECASE),
    ]
    
    # Sensitive keywords to flag
    SENSITIVE_KEYWORDS = [
        'password', 'token', 'secret', 'key', 'api_key',
        'aadhaar', 'session_token', 'otp_code'
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log records containing sensitive information.
        
        Args:
            record: The log record to filter
            
        Returns:
            bool: True if record should be logged, False if it should be filtered out
        """
        if not hasattr(record, 'getMessage'):
            return True
            
        message = str(record.getMessage()).lower()
        
        # Check for sensitive keywords
        for keyword in self.SENSITIVE_KEYWORDS:
            if keyword in message:
                # Instead of blocking, mask the sensitive data
                original_message = record.getMessage()
                masked_message = self._mask_sensitive_data(original_message)
                record.msg = masked_message
                record.args = ()
                break
        
        return True
    
    def _mask_sensitive_data(self, text: str) -> str:
        """
        Mask sensitive data in the text.
        
        Args:
            text: The text to mask
            
        Returns:
            str: Text with sensitive data masked
        """
        masked_text = text
        
        # Apply pattern-based masking
        for pattern in self.SENSITIVE_PATTERNS:
            masked_text = pattern.sub(lambda m: '*' * len(m.group()), masked_text)
        
        # Mask specific field patterns
        field_patterns = [
            (r'phone[_\s]*number?\s*[:=]\s*[^\s,}]+', 'phone_number: ****'),
            (r'email\s*[:=]\s*[^\s,}]+', 'email: ****@****.***'),
            (r'aadhaar[_\s]*number?\s*[:=]\s*[^\s,}]+', 'aadhaar_number: ****'),
            (r'password\s*[:=]\s*[^\s,}]+', 'password: ****'),
            (r'token\s*[:=]\s*[^\s,}]+', 'token: ****'),
        ]
        
        for pattern, replacement in field_patterns:
            masked_text = re.sub(pattern, replacement, masked_text, flags=re.IGNORECASE)
        
        return masked_text


class ProductionSafetyFilter(logging.Filter):
    """
    Additional filter for production environments to ensure no sensitive data leaks.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Strict filter for production use.
        
        Args:
            record: The log record to filter
            
        Returns:
            bool: True if record should be logged, False if it should be filtered out
        """
        if not hasattr(record, 'getMessage'):
            return True
            
        message = str(record.getMessage())
        
        # In production, be very strict about any personal data
        sensitive_indicators = [
            '@',  # Email indicator
            '+91',  # Indian phone prefix
            '91',   # Could be phone
            'aadhaar', 'aadhar',  # Aadhaar variations
            'otp',  # OTP codes
        ]
        
        message_lower = message.lower()
        for indicator in sensitive_indicators:
            if indicator in message_lower:
                # Replace the entire message with a generic one
                record.msg = f"[SECURITY] Sensitive data detected in log message - details masked"
                record.args = ()
                break
        
        return True