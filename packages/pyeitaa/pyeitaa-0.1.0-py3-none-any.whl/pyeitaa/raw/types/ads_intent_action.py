from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class AdsIntentAction(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.AdsClickAction`.

    Details:
        - Layer: ``135``
        - ID: ``0x93ea277``

    Parameters:
        uri: ``str``
    """

    __slots__: List[str] = ["uri"]

    ID = 0x93ea277
    QUALNAME = "types.AdsIntentAction"

    def __init__(self, *, uri: str) -> None:
        self.uri = uri  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        uri = String.read(data)
        
        return AdsIntentAction(uri=uri)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.uri))
        
        return data.getvalue()
