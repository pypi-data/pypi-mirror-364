from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class RpcError(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.RpcError`.

    Details:
        - Layer: ``135``
        - ID: ``0x2144ca19``

    Parameters:
        error_code: ``int`` ``32-bit``
        error_message: ``str``
    """

    __slots__: List[str] = ["error_code", "error_message"]

    ID = 0x2144ca19
    QUALNAME = "types.RpcError"

    def __init__(self, *, error_code: int, error_message: str) -> None:
        self.error_code = error_code  # int
        self.error_message = error_message  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        error_code = Int.read(data)
        
        error_message = String.read(data)
        
        return RpcError(error_code=error_code, error_message=error_message)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.error_code))
        
        data.write(String(self.error_message))
        
        return data.getvalue()
