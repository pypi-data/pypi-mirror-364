from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetConfig(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x3b06e795``

    **No parameters required.**

    Returns:
        :obj:`Config <pyeitaa.raw.base.Config>`
    """

    __slots__: List[str] = []

    ID = -0x3b06e795
    QUALNAME = "functions.help.GetConfig"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetConfig()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
