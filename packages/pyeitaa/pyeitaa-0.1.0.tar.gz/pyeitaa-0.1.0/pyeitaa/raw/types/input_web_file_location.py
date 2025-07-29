from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputWebFileLocation(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputWebFileLocation`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3dc6297a``

    Parameters:
        url: ``str``
        access_hash: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["url", "access_hash"]

    ID = -0x3dc6297a
    QUALNAME = "types.InputWebFileLocation"

    def __init__(self, *, url: str, access_hash: int) -> None:
        self.url = url  # string
        self.access_hash = access_hash  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        url = String.read(data)
        
        access_hash = Long.read(data)
        
        return InputWebFileLocation(url=url, access_hash=access_hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.url))
        
        data.write(Long(self.access_hash))
        
        return data.getvalue()
