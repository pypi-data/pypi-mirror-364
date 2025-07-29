from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class EncryptedChat(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.EncryptedChat`.

    Details:
        - Layer: ``135``
        - ID: ``0x61f0d4c7``

    Parameters:
        id: ``int`` ``32-bit``
        access_hash: ``int`` ``64-bit``
        date: ``int`` ``32-bit``
        admin_id: ``int`` ``64-bit``
        participant_id: ``int`` ``64-bit``
        g_a_or_b: ``bytes``
        key_fingerprint: ``int`` ``64-bit``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.RequestEncryption <pyeitaa.raw.functions.messages.RequestEncryption>`
            - :obj:`messages.AcceptEncryption <pyeitaa.raw.functions.messages.AcceptEncryption>`
    """

    __slots__: List[str] = ["id", "access_hash", "date", "admin_id", "participant_id", "g_a_or_b", "key_fingerprint"]

    ID = 0x61f0d4c7
    QUALNAME = "types.EncryptedChat"

    def __init__(self, *, id: int, access_hash: int, date: int, admin_id: int, participant_id: int, g_a_or_b: bytes, key_fingerprint: int) -> None:
        self.id = id  # int
        self.access_hash = access_hash  # long
        self.date = date  # int
        self.admin_id = admin_id  # long
        self.participant_id = participant_id  # long
        self.g_a_or_b = g_a_or_b  # bytes
        self.key_fingerprint = key_fingerprint  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Int.read(data)
        
        access_hash = Long.read(data)
        
        date = Int.read(data)
        
        admin_id = Long.read(data)
        
        participant_id = Long.read(data)
        
        g_a_or_b = Bytes.read(data)
        
        key_fingerprint = Long.read(data)
        
        return EncryptedChat(id=id, access_hash=access_hash, date=date, admin_id=admin_id, participant_id=participant_id, g_a_or_b=g_a_or_b, key_fingerprint=key_fingerprint)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.id))
        
        data.write(Long(self.access_hash))
        
        data.write(Int(self.date))
        
        data.write(Long(self.admin_id))
        
        data.write(Long(self.participant_id))
        
        data.write(Bytes(self.g_a_or_b))
        
        data.write(Long(self.key_fingerprint))
        
        return data.getvalue()
