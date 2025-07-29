from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class CdnFile(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.upload.CdnFile`.

    Details:
        - Layer: ``135``
        - ID: ``-0x566035b1``

    Parameters:
        bytes: ``bytes``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`upload.GetCdnFile <pyeitaa.raw.functions.upload.GetCdnFile>`
    """

    __slots__: List[str] = ["bytes"]

    ID = -0x566035b1
    QUALNAME = "types.upload.CdnFile"

    def __init__(self, *, bytes: bytes) -> None:
        self.bytes = bytes  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        bytes = Bytes.read(data)
        
        return CdnFile(bytes=bytes)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bytes(self.bytes))
        
        return data.getvalue()
