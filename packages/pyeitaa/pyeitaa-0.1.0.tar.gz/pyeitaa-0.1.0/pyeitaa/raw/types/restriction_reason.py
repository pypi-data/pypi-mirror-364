from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class RestrictionReason(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.RestrictionReason`.

    Details:
        - Layer: ``135``
        - ID: ``-0x2f8d534c``

    Parameters:
        platform: ``str``
        reason: ``str``
        text: ``str``
    """

    __slots__: List[str] = ["platform", "reason", "text"]

    ID = -0x2f8d534c
    QUALNAME = "types.RestrictionReason"

    def __init__(self, *, platform: str, reason: str, text: str) -> None:
        self.platform = platform  # string
        self.reason = reason  # string
        self.text = text  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        platform = String.read(data)
        
        reason = String.read(data)
        
        text = String.read(data)
        
        return RestrictionReason(platform=platform, reason=reason, text=text)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.platform))
        
        data.write(String(self.reason))
        
        data.write(String(self.text))
        
        return data.getvalue()
