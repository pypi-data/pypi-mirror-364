from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class Unblock(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x4159a2b0``

    Parameters:
        id: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["id"]

    ID = -0x4159a2b0
    QUALNAME = "functions.contacts.Unblock"

    def __init__(self, *, id: "raw.base.InputPeer") -> None:
        self.id = id  # InputPeer

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data)
        
        return Unblock(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.id.write())
        
        return data.getvalue()
