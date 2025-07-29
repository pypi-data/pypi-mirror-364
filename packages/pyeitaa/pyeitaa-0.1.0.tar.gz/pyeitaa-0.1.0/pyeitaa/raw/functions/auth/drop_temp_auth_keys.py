from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DropTempAuthKeys(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x71b75e78``

    Parameters:
        except_auth_keys: List of ``int`` ``64-bit``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["except_auth_keys"]

    ID = -0x71b75e78
    QUALNAME = "functions.auth.DropTempAuthKeys"

    def __init__(self, *, except_auth_keys: List[int]) -> None:
        self.except_auth_keys = except_auth_keys  # Vector<long>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        except_auth_keys = TLObject.read(data, Long)
        
        return DropTempAuthKeys(except_auth_keys=except_auth_keys)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.except_auth_keys, Long))
        
        return data.getvalue()
