from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class LiveGetMedia(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.LiveGetMedia`.

    Details:
        - Layer: ``135``
        - ID: ``0x4731a7ba``

    Parameters:
        flags: ``int`` ``32-bit``
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`LiveGetMedia <pyeitaa.raw.functions.LiveGetMedia>`
    """

    __slots__: List[str] = ["flags", "id", "access_hash"]

    ID = 0x4731a7ba
    QUALNAME = "types.LiveGetMedia"

    def __init__(self, *, flags: int, id: int, access_hash: int) -> None:
        self.flags = flags  # int
        self.id = id  # long
        self.access_hash = access_hash  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        flags = Int.read(data)
        
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        return LiveGetMedia(flags=flags, id=id, access_hash=access_hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.flags))
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        return data.getvalue()
