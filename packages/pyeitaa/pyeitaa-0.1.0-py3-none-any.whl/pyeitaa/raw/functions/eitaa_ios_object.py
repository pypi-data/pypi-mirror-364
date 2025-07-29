from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class EitaaIosObject(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x71c2d22c``

    Parameters:
        token: ``str``
        imei: ``str``
        packed_data: ``bytes``
        layer: ``int`` ``32-bit``
        build_version: ``int`` ``32-bit``

    Returns:
        :obj:`EitaaIosObject <pyeitaa.raw.base.EitaaIosObject>`
    """

    __slots__: List[str] = ["token", "imei", "packed_data", "layer", "build_version"]

    ID = 0x71c2d22c
    QUALNAME = "functions.EitaaIosObject"

    def __init__(self, *, token: str, imei: str, packed_data: bytes, layer: int, build_version: int) -> None:
        self.token = token  # string
        self.imei = imei  # string
        self.packed_data = packed_data  # bytes
        self.layer = layer  # int
        self.build_version = build_version  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        
        token = String.read(data)
        
        imei = String.read(data)
        flags = Int.read(data)
        
        packed_data = Bytes.read(data)
        
        layer = Int.read(data)
        
        build_version = Int.read(data)
        
        return EitaaIosObject(token=token, imei=imei, packed_data=packed_data, layer=layer, build_version=build_version)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        
        data.write(String(self.token))
        
        data.write(String(self.imei))
        flags = 0
        
        data.write(Int(flags))
        
        data.write(Bytes(self.packed_data))
        
        data.write(Int(self.layer))
        
        data.write(Int(self.build_version))
        
        return data.getvalue()
