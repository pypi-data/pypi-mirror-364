from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class DeleteMessages(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x1a716a2e``

    Parameters:
        id: List of ``int`` ``32-bit``
        revoke (optional): ``bool``

    Returns:
        :obj:`messages.AffectedMessages <pyeitaa.raw.base.messages.AffectedMessages>`
    """

    __slots__: List[str] = ["id", "revoke"]

    ID = -0x1a716a2e
    QUALNAME = "functions.messages.DeleteMessages"

    def __init__(self, *, id: List[int], revoke: Optional[bool] = None) -> None:
        self.id = id  # Vector<int>
        self.revoke = revoke  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        revoke = True if flags & (1 << 0) else False
        id = TLObject.read(data, Int)
        
        return DeleteMessages(id=id, revoke=revoke)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.revoke else 0
        data.write(Int(flags))
        
        data.write(Vector(self.id, Int))
        
        return data.getvalue()
