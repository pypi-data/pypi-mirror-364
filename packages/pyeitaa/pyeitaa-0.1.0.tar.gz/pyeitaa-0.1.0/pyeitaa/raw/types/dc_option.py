from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class DcOption(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.DcOption`.

    Details:
        - Layer: ``135``
        - ID: ``0x18b7a10d``

    Parameters:
        id: ``int`` ``32-bit``
        ip_address: ``str``
        port: ``int`` ``32-bit``
        ipv6 (optional): ``bool``
        media_only (optional): ``bool``
        tcpo_only (optional): ``bool``
        cdn (optional): ``bool``
        static (optional): ``bool``
        secret (optional): ``bytes``
    """

    __slots__: List[str] = ["id", "ip_address", "port", "ipv6", "media_only", "tcpo_only", "cdn", "static", "secret"]

    ID = 0x18b7a10d
    QUALNAME = "types.DcOption"

    def __init__(self, *, id: int, ip_address: str, port: int, ipv6: Optional[bool] = None, media_only: Optional[bool] = None, tcpo_only: Optional[bool] = None, cdn: Optional[bool] = None, static: Optional[bool] = None, secret: Optional[bytes] = None) -> None:
        self.id = id  # int
        self.ip_address = ip_address  # string
        self.port = port  # int
        self.ipv6 = ipv6  # flags.0?true
        self.media_only = media_only  # flags.1?true
        self.tcpo_only = tcpo_only  # flags.2?true
        self.cdn = cdn  # flags.3?true
        self.static = static  # flags.4?true
        self.secret = secret  # flags.10?bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        ipv6 = True if flags & (1 << 0) else False
        media_only = True if flags & (1 << 1) else False
        tcpo_only = True if flags & (1 << 2) else False
        cdn = True if flags & (1 << 3) else False
        static = True if flags & (1 << 4) else False
        id = Int.read(data)
        
        ip_address = String.read(data)
        
        port = Int.read(data)
        
        secret = Bytes.read(data) if flags & (1 << 10) else None
        return DcOption(id=id, ip_address=ip_address, port=port, ipv6=ipv6, media_only=media_only, tcpo_only=tcpo_only, cdn=cdn, static=static, secret=secret)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.ipv6 else 0
        flags |= (1 << 1) if self.media_only else 0
        flags |= (1 << 2) if self.tcpo_only else 0
        flags |= (1 << 3) if self.cdn else 0
        flags |= (1 << 4) if self.static else 0
        flags |= (1 << 10) if self.secret is not None else 0
        data.write(Int(flags))
        
        data.write(Int(self.id))
        
        data.write(String(self.ip_address))
        
        data.write(Int(self.port))
        
        if self.secret is not None:
            data.write(Bytes(self.secret))
        
        return data.getvalue()
