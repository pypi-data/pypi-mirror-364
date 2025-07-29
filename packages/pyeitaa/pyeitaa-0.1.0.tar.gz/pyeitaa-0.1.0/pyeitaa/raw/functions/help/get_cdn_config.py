from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetCdnConfig(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x52029342``

    **No parameters required.**

    Returns:
        :obj:`CdnConfig <pyeitaa.raw.base.CdnConfig>`
    """

    __slots__: List[str] = []

    ID = 0x52029342
    QUALNAME = "functions.help.GetCdnConfig"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetCdnConfig()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
