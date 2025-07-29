from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class EncryptedChatEmpty(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.EncryptedChat`.

    Details:
        - Layer: ``135``
        - ID: ``-0x54813f60``

    Parameters:
        id: ``int`` ``32-bit``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.RequestEncryption <pyeitaa.raw.functions.messages.RequestEncryption>`
            - :obj:`messages.AcceptEncryption <pyeitaa.raw.functions.messages.AcceptEncryption>`
    """

    __slots__: List[str] = ["id"]

    ID = -0x54813f60
    QUALNAME = "types.EncryptedChatEmpty"

    def __init__(self, *, id: int) -> None:
        self.id = id  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Int.read(data)
        
        return EncryptedChatEmpty(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.id))
        
        return data.getvalue()
