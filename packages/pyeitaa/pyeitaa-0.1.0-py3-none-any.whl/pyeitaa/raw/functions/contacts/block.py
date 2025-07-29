from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class Block(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x68cc1411``

    Parameters:
        id: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["id"]

    ID = 0x68cc1411
    QUALNAME = "functions.contacts.Block"

    def __init__(self, *, id: "raw.base.InputPeer") -> None:
        self.id = id  # InputPeer

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = TLObject.read(data)
        
        return Block(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.id.write())
        
        return data.getvalue()
