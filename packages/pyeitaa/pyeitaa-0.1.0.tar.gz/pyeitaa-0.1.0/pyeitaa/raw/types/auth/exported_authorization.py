from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ExportedAuthorization(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.auth.ExportedAuthorization`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4bcb1d48``

    Parameters:
        id: ``int`` ``64-bit``
        bytes: ``bytes``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`auth.ExportAuthorization <pyeitaa.raw.functions.auth.ExportAuthorization>`
    """

    __slots__: List[str] = ["id", "bytes"]

    ID = -0x4bcb1d48
    QUALNAME = "types.auth.ExportedAuthorization"

    def __init__(self, *, id: int, bytes: bytes) -> None:
        self.id = id  # long
        self.bytes = bytes  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        bytes = Bytes.read(data)
        
        return ExportedAuthorization(id=id, bytes=bytes)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        data.write(Bytes(self.bytes))
        
        return data.getvalue()
