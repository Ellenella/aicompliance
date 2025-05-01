from datetime import datetime
import hashlib

class GDPRHandler:
    @staticmethod
    def anonymize(text):
        return hashlib.sha256(text.encode()).hexdigest()[:10]
    
    @staticmethod
    def validate_retention_period(days):
        return 0 <= days <= 30  # GDPR default max retention
    
    @staticmethod
    def generate_consent_form():
        return """
        GDPR Consent Form
        [ ] I consent to temporary processing (24h)
        [ ] I consent to long-term storage (30d)
        """