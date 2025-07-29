from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetGlobalPrivacySettings(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x14d4b30a``

    **No parameters required.**

    Returns:
        :obj:`GlobalPrivacySettings <pyeitaa.raw.base.GlobalPrivacySettings>`
    """

    __slots__: List[str] = []

    ID = -0x14d4b30a
    QUALNAME = "functions.account.GetGlobalPrivacySettings"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetGlobalPrivacySettings()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
