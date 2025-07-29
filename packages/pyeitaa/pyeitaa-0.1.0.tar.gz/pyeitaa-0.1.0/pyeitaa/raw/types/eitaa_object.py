from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class EitaaObject(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.EitaaObject`.

    Details:
        - Layer: ``135``
        - ID: ``0x7abe77ed``

    Parameters:
        token: ``str``
        imei: ``str``
        packed_data: ``bytes``
        layer: ``int`` ``32-bit``
        flags: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`EitaaObject <pyeitaa.raw.functions.EitaaObject>`
    """

    __slots__: List[str] = ["token", "imei", "packed_data", "layer", "flags"]

    ID = 0x7abe77ed
    QUALNAME = "types.EitaaObject"

    def __init__(self, *, token: str, imei: str, packed_data: bytes, layer: int, flags: int) -> None:
        self.token = token  # string
        self.imei = imei  # string
        self.packed_data = packed_data  # bytes
        self.layer = layer  # int
        self.flags = flags  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        token = String.read(data)
        
        imei = String.read(data)
        
        packed_data = Bytes.read(data)
        
        layer = Int.read(data)
        
        flags = Int.read(data)
        
        return EitaaObject(token=token, imei=imei, packed_data=packed_data, layer=layer, flags=flags)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.token))
        
        data.write(String(self.imei))
        
        data.write(Bytes(self.packed_data))
        
        data.write(Int(self.layer))
        
        data.write(Int(self.flags))
        
        return data.getvalue()
