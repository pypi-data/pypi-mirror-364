from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class UserPayHash(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.UserPayHash`.

    Details:
        - Layer: ``135``
        - ID: ``-0x41502153``

    Parameters:
        flag: ``int`` ``32-bit``
        hash: ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`GetPayHash <pyeitaa.raw.functions.GetPayHash>`
    """

    __slots__: List[str] = ["flag", "hash"]

    ID = -0x41502153
    QUALNAME = "types.UserPayHash"

    def __init__(self, *, flag: int, hash: str) -> None:
        self.flag = flag  # int
        self.hash = hash  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        flag = Int.read(data)
        
        hash = String.read(data)
        
        return UserPayHash(flag=flag, hash=hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.flag))
        
        data.write(String(self.hash))
        
        return data.getvalue()
