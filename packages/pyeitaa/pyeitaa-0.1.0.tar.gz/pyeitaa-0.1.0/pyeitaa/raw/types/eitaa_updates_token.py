from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class EitaaUpdatesToken(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.EitaaUpdatesToken`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5a93e5cf``

    Parameters:
        token: ``str``
        expire: ``int`` ``32-bit``
        date: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["token", "expire", "date"]

    ID = -0x5a93e5cf
    QUALNAME = "types.EitaaUpdatesToken"

    def __init__(self, *, token: str, expire: int, date: int) -> None:
        self.token = token  # string
        self.expire = expire  # int
        self.date = date  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        token = String.read(data)
        
        expire = Int.read(data)
        
        date = Int.read(data)
        
        return EitaaUpdatesToken(token=token, expire=expire, date=date)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.token))
        
        data.write(Int(self.expire))
        
        data.write(Int(self.date))
        
        return data.getvalue()
