from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class FileHash(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.FileHash`.

    Details:
        - Layer: ``135``
        - ID: ``0x6242c773``

    Parameters:
        offset: ``int`` ``32-bit``
        limit: ``int`` ``32-bit``
        hash: ``bytes``

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`upload.ReuploadCdnFile <pyeitaa.raw.functions.upload.ReuploadCdnFile>`
            - :obj:`upload.GetCdnFileHashes <pyeitaa.raw.functions.upload.GetCdnFileHashes>`
            - :obj:`upload.GetFileHashes <pyeitaa.raw.functions.upload.GetFileHashes>`
    """

    __slots__: List[str] = ["offset", "limit", "hash"]

    ID = 0x6242c773
    QUALNAME = "types.FileHash"

    def __init__(self, *, offset: int, limit: int, hash: bytes) -> None:
        self.offset = offset  # int
        self.limit = limit  # int
        self.hash = hash  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        offset = Int.read(data)
        
        limit = Int.read(data)
        
        hash = Bytes.read(data)
        
        return FileHash(offset=offset, limit=limit, hash=hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.offset))
        
        data.write(Int(self.limit))
        
        data.write(Bytes(self.hash))
        
        return data.getvalue()
