from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputCheckPasswordSRP(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputCheckPasswordSRP`.

    Details:
        - Layer: ``135``
        - ID: ``-0x2d800f7e``

    Parameters:
        srp_id: ``int`` ``64-bit``
        A: ``bytes``
        M1: ``bytes``
    """

    __slots__: List[str] = ["srp_id", "A", "M1"]

    ID = -0x2d800f7e
    QUALNAME = "types.InputCheckPasswordSRP"

    def __init__(self, *, srp_id: int, A: bytes, M1: bytes) -> None:
        self.srp_id = srp_id  # long
        self.A = A  # bytes
        self.M1 = M1  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        srp_id = Long.read(data)
        
        A = Bytes.read(data)
        
        M1 = Bytes.read(data)
        
        return InputCheckPasswordSRP(srp_id=srp_id, A=A, M1=M1)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.srp_id))
        
        data.write(Bytes(self.A))
        
        data.write(Bytes(self.M1))
        
        return data.getvalue()
