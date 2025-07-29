from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class PhoneCallProtocol(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PhoneCallProtocol`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3787038``

    Parameters:
        min_layer: ``int`` ``32-bit``
        max_layer: ``int`` ``32-bit``
        library_versions: List of ``str``
        udp_p2p (optional): ``bool``
        udp_reflector (optional): ``bool``
    """

    __slots__: List[str] = ["min_layer", "max_layer", "library_versions", "udp_p2p", "udp_reflector"]

    ID = -0x3787038
    QUALNAME = "types.PhoneCallProtocol"

    def __init__(self, *, min_layer: int, max_layer: int, library_versions: List[str], udp_p2p: Optional[bool] = None, udp_reflector: Optional[bool] = None) -> None:
        self.min_layer = min_layer  # int
        self.max_layer = max_layer  # int
        self.library_versions = library_versions  # Vector<string>
        self.udp_p2p = udp_p2p  # flags.0?true
        self.udp_reflector = udp_reflector  # flags.1?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        udp_p2p = True if flags & (1 << 0) else False
        udp_reflector = True if flags & (1 << 1) else False
        min_layer = Int.read(data)
        
        max_layer = Int.read(data)
        
        library_versions = TLObject.read(data, String)
        
        return PhoneCallProtocol(min_layer=min_layer, max_layer=max_layer, library_versions=library_versions, udp_p2p=udp_p2p, udp_reflector=udp_reflector)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.udp_p2p else 0
        flags |= (1 << 1) if self.udp_reflector else 0
        data.write(Int(flags))
        
        data.write(Int(self.min_layer))
        
        data.write(Int(self.max_layer))
        
        data.write(Vector(self.library_versions, String))
        
        return data.getvalue()
