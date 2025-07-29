from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class CdnPublicKey(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.CdnPublicKey`.

    Details:
        - Layer: ``135``
        - ID: ``-0x367d1546``

    Parameters:
        dc_id: ``int`` ``32-bit``
        public_key: ``str``
    """

    __slots__: List[str] = ["dc_id", "public_key"]

    ID = -0x367d1546
    QUALNAME = "types.CdnPublicKey"

    def __init__(self, *, dc_id: int, public_key: str) -> None:
        self.dc_id = dc_id  # int
        self.public_key = public_key  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        dc_id = Int.read(data)
        
        public_key = String.read(data)
        
        return CdnPublicKey(dc_id=dc_id, public_key=public_key)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.dc_id))
        
        data.write(String(self.public_key))
        
        return data.getvalue()
