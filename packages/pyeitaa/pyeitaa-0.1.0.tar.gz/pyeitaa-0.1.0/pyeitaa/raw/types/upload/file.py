from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class File(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.upload.File`.

    Details:
        - Layer: ``135``
        - ID: ``0x96a18d5``

    Parameters:
        type: :obj:`storage.FileType <pyeitaa.raw.base.storage.FileType>`
        mtime: ``int`` ``32-bit``
        bytes: ``bytes``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`upload.GetFile <pyeitaa.raw.functions.upload.GetFile>`
            - :obj:`upload.GetFile2 <pyeitaa.raw.functions.upload.GetFile2>`
    """

    __slots__: List[str] = ["type", "mtime", "bytes"]

    ID = 0x96a18d5
    QUALNAME = "types.upload.File"

    def __init__(self, *, type: "raw.base.storage.FileType", mtime: int, bytes: bytes) -> None:
        self.type = type  # storage.FileType
        self.mtime = mtime  # int
        self.bytes = bytes  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        type = TLObject.read(data)
        
        mtime = Int.read(data)
        
        bytes = Bytes.read(data)
        
        return File(type=type, mtime=mtime, bytes=bytes)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.type.write())
        
        data.write(Int(self.mtime))
        
        data.write(Bytes(self.bytes))
        
        return data.getvalue()
