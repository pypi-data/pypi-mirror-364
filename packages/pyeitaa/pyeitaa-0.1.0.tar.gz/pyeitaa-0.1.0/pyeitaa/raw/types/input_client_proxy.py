from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputClientProxy(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputClientProxy`.

    Details:
        - Layer: ``135``
        - ID: ``0x75588b3f``

    Parameters:
        address: ``str``
        port: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["address", "port"]

    ID = 0x75588b3f
    QUALNAME = "types.InputClientProxy"

    def __init__(self, *, address: str, port: int) -> None:
        self.address = address  # string
        self.port = port  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        address = String.read(data)
        
        port = Int.read(data)
        
        return InputClientProxy(address=address, port=port)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.address))
        
        data.write(Int(self.port))
        
        return data.getvalue()
