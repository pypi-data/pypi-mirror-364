from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class EncryptedFile(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.EncryptedFile`.

    Details:
        - Layer: ``135``
        - ID: ``0x4a70994c``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
        size: ``int`` ``32-bit``
        dc_id: ``int`` ``32-bit``
        key_fingerprint: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.UploadEncryptedFile <pyeitaa.raw.functions.messages.UploadEncryptedFile>`
    """

    __slots__: List[str] = ["id", "access_hash", "size", "dc_id", "key_fingerprint"]

    ID = 0x4a70994c
    QUALNAME = "types.EncryptedFile"

    def __init__(self, *, id: int, access_hash: int, size: int, dc_id: int, key_fingerprint: int) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.size = size  # int
        self.dc_id = dc_id  # int
        self.key_fingerprint = key_fingerprint  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        size = Int.read(data)
        
        dc_id = Int.read(data)
        
        key_fingerprint = Int.read(data)
        
        return EncryptedFile(id=id, access_hash=access_hash, size=size, dc_id=dc_id, key_fingerprint=key_fingerprint)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        data.write(Int(self.size))
        
        data.write(Int(self.dc_id))
        
        data.write(Int(self.key_fingerprint))
        
        return data.getvalue()
