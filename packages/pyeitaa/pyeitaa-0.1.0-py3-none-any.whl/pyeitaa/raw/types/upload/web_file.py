from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class WebFile(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.upload.WebFile`.

    Details:
        - Layer: ``135``
        - ID: ``0x21e753bc``

    Parameters:
        size: ``int`` ``32-bit``
        mime_type: ``str``
        file_type: :obj:`storage.FileType <pyeitaa.raw.base.storage.FileType>`
        mtime: ``int`` ``32-bit``
        bytes: ``bytes``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`upload.GetWebFile <pyeitaa.raw.functions.upload.GetWebFile>`
    """

    __slots__: List[str] = ["size", "mime_type", "file_type", "mtime", "bytes"]

    ID = 0x21e753bc
    QUALNAME = "types.upload.WebFile"

    def __init__(self, *, size: int, mime_type: str, file_type: "raw.base.storage.FileType", mtime: int, bytes: bytes) -> None:
        self.size = size  # int
        self.mime_type = mime_type  # string
        self.file_type = file_type  # storage.FileType
        self.mtime = mtime  # int
        self.bytes = bytes  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        size = Int.read(data)
        
        mime_type = String.read(data)
        
        file_type = TLObject.read(data)
        
        mtime = Int.read(data)
        
        bytes = Bytes.read(data)
        
        return WebFile(size=size, mime_type=mime_type, file_type=file_type, mtime=mtime, bytes=bytes)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.size))
        
        data.write(String(self.mime_type))
        
        data.write(self.file_type.write())
        
        data.write(Int(self.mtime))
        
        data.write(Bytes(self.bytes))
        
        return data.getvalue()
