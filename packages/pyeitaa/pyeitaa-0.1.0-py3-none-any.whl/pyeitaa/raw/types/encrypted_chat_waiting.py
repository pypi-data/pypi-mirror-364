from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class EncryptedChatWaiting(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.EncryptedChat`.

    Details:
        - Layer: ``135``
        - ID: ``0x66b25953``

    Parameters:
        id: ``int`` ``32-bit``
        access_hash: ``int`` ``64-bit``
        date: ``int`` ``32-bit``
        admin_id: ``int`` ``64-bit``
        participant_id: ``int`` ``64-bit``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.RequestEncryption <pyeitaa.raw.functions.messages.RequestEncryption>`
            - :obj:`messages.AcceptEncryption <pyeitaa.raw.functions.messages.AcceptEncryption>`
    """

    __slots__: List[str] = ["id", "access_hash", "date", "admin_id", "participant_id"]

    ID = 0x66b25953
    QUALNAME = "types.EncryptedChatWaiting"

    def __init__(self, *, id: int, access_hash: int, date: int, admin_id: int, participant_id: int) -> None:
        self.id = id  # int
        self.access_hash = access_hash  # long
        self.date = date  # int
        self.admin_id = admin_id  # long
        self.participant_id = participant_id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Int.read(data)
        
        access_hash = Long.read(data)
        
        date = Int.read(data)
        
        admin_id = Long.read(data)
        
        participant_id = Long.read(data)
        
        return EncryptedChatWaiting(id=id, access_hash=access_hash, date=date, admin_id=admin_id, participant_id=participant_id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.id))
        
        data.write(Long(self.access_hash))
        
        data.write(Int(self.date))
        
        data.write(Long(self.admin_id))
        
        data.write(Long(self.participant_id))
        
        return data.getvalue()
