from .auto_name import AutoName
from ..raw.types.auth import (
    CodeTypeSms,
    CodeTypeCall,
    CodeTypeFlashCall
)


class NextCodeType(AutoName):
    """Sent code type enumeration used in :obj:`~pyeitaa.types.SentCode`."""

    CALL = CodeTypeCall
    "The code will be sent via a phone call. A synthesized voice will tell the user which verification code to input."

    FLASH_CALL = CodeTypeFlashCall
    "The code will be sent via a flash phone call, that will be closed immediately."

    SMS = CodeTypeSms
    "The code will be sent via SMS."