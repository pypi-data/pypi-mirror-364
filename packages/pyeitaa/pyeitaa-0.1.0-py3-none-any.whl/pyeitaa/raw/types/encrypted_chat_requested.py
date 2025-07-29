from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class EncryptedChatRequested(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.EncryptedChat`.

    Details:
        - Layer: ``135``
        - ID: ``0x48f1d94c``

    Parameters:
        id: ``int`` ``32-bit``
        access_hash: ``int`` ``64-bit``
        date: ``int`` ``32-bit``
        admin_id: ``int`` ``64-bit``
        participant_id: ``int`` ``64-bit``
        g_a: ``bytes``
        folder_id (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.RequestEncryption <pyeitaa.raw.functions.messages.RequestEncryption>`
            - :obj:`messages.AcceptEncryption <pyeitaa.raw.functions.messages.AcceptEncryption>`
    """

    __slots__: List[str] = ["id", "access_hash", "date", "admin_id", "participant_id", "g_a", "folder_id"]

    ID = 0x48f1d94c
    QUALNAME = "types.EncryptedChatRequested"

    def __init__(self, *, id: int, access_hash: int, date: int, admin_id: int, participant_id: int, g_a: bytes, folder_id: Optional[int] = None) -> None:
        self.id = id  # int
        self.access_hash = access_hash  # long
        self.date = date  # int
        self.admin_id = admin_id  # long
        self.participant_id = participant_id  # long
        self.g_a = g_a  # bytes
        self.folder_id = folder_id  # flags.0?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        folder_id = Int.read(data) if flags & (1 << 0) else None
        id = Int.read(data)
        
        access_hash = Long.read(data)
        
        date = Int.read(data)
        
        admin_id = Long.read(data)
        
        participant_id = Long.read(data)
        
        g_a = Bytes.read(data)
        
        return EncryptedChatRequested(id=id, access_hash=access_hash, date=date, admin_id=admin_id, participant_id=participant_id, g_a=g_a, folder_id=folder_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.folder_id is not None else 0
        data.write(Int(flags))
        
        if self.folder_id is not None:
            data.write(Int(self.folder_id))
        
        data.write(Int(self.id))
        
        data.write(Long(self.access_hash))
        
        data.write(Int(self.date))
        
        data.write(Long(self.admin_id))
        
        data.write(Long(self.participant_id))
        
        data.write(Bytes(self.g_a))
        
        return data.getvalue()
