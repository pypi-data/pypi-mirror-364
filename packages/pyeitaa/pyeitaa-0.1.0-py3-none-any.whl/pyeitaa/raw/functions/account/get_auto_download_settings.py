from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetAutoDownloadSettings(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x56da0b3f``

    **No parameters required.**

    Returns:
        :obj:`account.AutoDownloadSettings <pyeitaa.raw.base.account.AutoDownloadSettings>`
    """

    __slots__: List[str] = []

    ID = 0x56da0b3f
    QUALNAME = "functions.account.GetAutoDownloadSettings"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetAutoDownloadSettings()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
