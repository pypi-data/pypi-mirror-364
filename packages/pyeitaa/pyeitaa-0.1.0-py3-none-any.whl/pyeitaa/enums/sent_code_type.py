from .auto_name import AutoName
from ..raw.types.auth import (
    SentCodeTypeSms,
    SentCodeTypeApp,
    SentCodeTypeCall,
    SentCodeTypeFlashCall
)


class SentCodeType(AutoName):
    """Sent code type enumeration used in :obj:`~pyeitaa.types.SentCode`."""

    APP = SentCodeTypeApp
    "The code was sent through the eitaa app."

    CALL = SentCodeTypeCall
    "The code will be sent via a phone call. A synthesized voice will tell the user which verification code to input."

    FLASH_CALL = SentCodeTypeFlashCall
    "The code will be sent via a flash phone call, that will be closed immediately."

    SMS = SentCodeTypeSms
    "The code was sent via SMS."