from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PeerSelfLocated(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PeerLocated`.

    Details:
        - Layer: ``135``
        - ID: ``-0x713d7b5``

    Parameters:
        expires: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["expires"]

    ID = -0x713d7b5
    QUALNAME = "types.PeerSelfLocated"

    def __init__(self, *, expires: int) -> None:
        self.expires = expires  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        expires = Int.read(data)
        
        return PeerSelfLocated(expires=expires)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.expires))
        
        return data.getvalue()
