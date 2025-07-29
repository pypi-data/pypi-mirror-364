from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class PhoneConnectionWebrtc(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PhoneConnection`.

    Details:
        - Layer: ``135``
        - ID: ``0x635fe375``

    Parameters:
        id: ``int`` ``64-bit``
        ip: ``str``
        ipv6: ``str``
        port: ``int`` ``32-bit``
        username: ``str``
        password: ``str``
        turn (optional): ``bool``
        stun (optional): ``bool``
    """

    __slots__: List[str] = ["id", "ip", "ipv6", "port", "username", "password", "turn", "stun"]

    ID = 0x635fe375
    QUALNAME = "types.PhoneConnectionWebrtc"

    def __init__(self, *, id: int, ip: str, ipv6: str, port: int, username: str, password: str, turn: Optional[bool] = None, stun: Optional[bool] = None) -> None:
        self.id = id  # long
        self.ip = ip  # string
        self.ipv6 = ipv6  # string
        self.port = port  # int
        self.username = username  # string
        self.password = password  # string
        self.turn = turn  # flags.0?true
        self.stun = stun  # flags.1?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        turn = True if flags & (1 << 0) else False
        stun = True if flags & (1 << 1) else False
        id = Long.read(data)
        
        ip = String.read(data)
        
        ipv6 = String.read(data)
        
        port = Int.read(data)
        
        username = String.read(data)
        
        password = String.read(data)
        
        return PhoneConnectionWebrtc(id=id, ip=ip, ipv6=ipv6, port=port, username=username, password=password, turn=turn, stun=stun)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.turn else 0
        flags |= (1 << 1) if self.stun else 0
        data.write(Int(flags))
        
        data.write(Long(self.id))
        
        data.write(String(self.ip))
        
        data.write(String(self.ipv6))
        
        data.write(Int(self.port))
        
        data.write(String(self.username))
        
        data.write(String(self.password))
        
        return data.getvalue()
