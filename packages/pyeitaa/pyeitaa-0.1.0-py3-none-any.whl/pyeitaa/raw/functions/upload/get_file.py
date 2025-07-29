from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class GetFile(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x4ea56504``

    Parameters:
        location: :obj:`InputFileLocation <pyeitaa.raw.base.InputFileLocation>`
        offset: ``int`` ``32-bit``
        limit: ``int`` ``32-bit``
        precise (optional): ``bool``
        cdn_supported (optional): ``bool``

    Returns:
        :obj:`upload.File <pyeitaa.raw.base.upload.File>`
    """

    __slots__: List[str] = ["location", "offset", "limit", "precise", "cdn_supported"]

    ID = -0x4ea56504
    QUALNAME = "functions.upload.GetFile"

    def __init__(self, *, location: "raw.base.InputFileLocation", offset: int, limit: int, precise: Optional[bool] = None, cdn_supported: Optional[bool] = None) -> None:
        self.location = location  # InputFileLocation
        self.offset = offset  # int
        self.limit = limit  # int
        self.precise = precise  # flags.0?true
        self.cdn_supported = cdn_supported  # flags.1?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        precise = True if flags & (1 << 0) else False
        cdn_supported = True if flags & (1 << 1) else False
        location = TLObject.read(data)
        
        offset = Int.read(data)
        
        limit = Int.read(data)
        
        return GetFile(location=location, offset=offset, limit=limit, precise=precise, cdn_supported=cdn_supported)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.precise else 0
        flags |= (1 << 1) if self.cdn_supported else 0
        data.write(Int(flags))
        
        data.write(self.location.write())
        
        data.write(Int(self.offset))
        
        data.write(Int(self.limit))
        
        return data.getvalue()
