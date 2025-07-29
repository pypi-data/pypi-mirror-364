from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class CdnFileReuploadNeeded(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.upload.CdnFile`.

    Details:
        - Layer: ``135``
        - ID: ``-0x11571b92``

    Parameters:
        request_token: ``bytes``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`upload.GetCdnFile <pyeitaa.raw.functions.upload.GetCdnFile>`
    """

    __slots__: List[str] = ["request_token"]

    ID = -0x11571b92
    QUALNAME = "types.upload.CdnFileReuploadNeeded"

    def __init__(self, *, request_token: bytes) -> None:
        self.request_token = request_token  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        request_token = Bytes.read(data)
        
        return CdnFileReuploadNeeded(request_token=request_token)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Bytes(self.request_token))
        
        return data.getvalue()
