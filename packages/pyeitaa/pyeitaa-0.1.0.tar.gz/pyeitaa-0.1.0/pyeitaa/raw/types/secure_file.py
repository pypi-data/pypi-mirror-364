from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SecureFile(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SecureFile`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1fd8859e``

    Parameters:
        id: ``int`` ``64-bit``
        access_hash: ``int`` ``64-bit``
        size: ``int`` ``32-bit``
        dc_id: ``int`` ``32-bit``
        date: ``int`` ``32-bit``
        file_hash: ``bytes``
        secret: ``bytes``
    """

    __slots__: List[str] = ["id", "access_hash", "size", "dc_id", "date", "file_hash", "secret"]

    ID = -0x1fd8859e
    QUALNAME = "types.SecureFile"

    def __init__(self, *, id: int, access_hash: int, size: int, dc_id: int, date: int, file_hash: bytes, secret: bytes) -> None:
        self.id = id  # long
        self.access_hash = access_hash  # long
        self.size = size  # int
        self.dc_id = dc_id  # int
        self.date = date  # int
        self.file_hash = file_hash  # bytes
        self.secret = secret  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        access_hash = Long.read(data)
        
        size = Int.read(data)
        
        dc_id = Int.read(data)
        
        date = Int.read(data)
        
        file_hash = Bytes.read(data)
        
        secret = Bytes.read(data)
        
        return SecureFile(id=id, access_hash=access_hash, size=size, dc_id=dc_id, date=date, file_hash=file_hash, secret=secret)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        data.write(Long(self.access_hash))
        
        data.write(Int(self.size))
        
        data.write(Int(self.dc_id))
        
        data.write(Int(self.date))
        
        data.write(Bytes(self.file_hash))
        
        data.write(Bytes(self.secret))
        
        return data.getvalue()
