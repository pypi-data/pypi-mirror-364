from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class EncryptedChatDiscarded(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.EncryptedChat`.

    Details:
        - Layer: ``135``
        - ID: ``0x1e1c7c45``

    Parameters:
        id: ``int`` ``32-bit``
        history_deleted (optional): ``bool``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.RequestEncryption <pyeitaa.raw.functions.messages.RequestEncryption>`
            - :obj:`messages.AcceptEncryption <pyeitaa.raw.functions.messages.AcceptEncryption>`
    """

    __slots__: List[str] = ["id", "history_deleted"]

    ID = 0x1e1c7c45
    QUALNAME = "types.EncryptedChatDiscarded"

    def __init__(self, *, id: int, history_deleted: Optional[bool] = None) -> None:
        self.id = id  # int
        self.history_deleted = history_deleted  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        history_deleted = True if flags & (1 << 0) else False
        id = Int.read(data)
        
        return EncryptedChatDiscarded(id=id, history_deleted=history_deleted)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.history_deleted else 0
        data.write(Int(flags))
        
        data.write(Int(self.id))
        
        return data.getvalue()
