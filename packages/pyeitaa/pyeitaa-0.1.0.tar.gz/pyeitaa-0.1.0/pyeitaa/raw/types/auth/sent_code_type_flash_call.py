from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SentCodeTypeFlashCall(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.auth.SentCodeType`.

    Details:
        - Layer: ``135``
        - ID: ``-0x54fc3927``

    Parameters:
        pattern: ``str``
    """

    __slots__: List[str] = ["pattern"]

    ID = -0x54fc3927
    QUALNAME = "types.auth.SentCodeTypeFlashCall"

    def __init__(self, *, pattern: str) -> None:
        self.pattern = pattern  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        pattern = String.read(data)
        
        return SentCodeTypeFlashCall(pattern=pattern)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.pattern))
        
        return data.getvalue()
