from enum import Enum


class VerificationChannel(str, Enum):
    """Canal por onde o código de verificação de posse é entregue."""
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    SMS = "SMS"
