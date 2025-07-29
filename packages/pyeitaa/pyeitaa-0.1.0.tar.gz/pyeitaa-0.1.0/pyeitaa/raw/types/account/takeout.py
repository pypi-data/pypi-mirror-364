from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class Takeout(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.account.Takeout`.

    Details:
        - Layer: ``135``
        - ID: ``0x4dba4501``

    Parameters:
        id: ``int`` ``64-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.InitTakeoutSession <pyeitaa.raw.functions.account.InitTakeoutSession>`
    """

    __slots__: List[str] = ["id"]

    ID = 0x4dba4501
    QUALNAME = "types.account.Takeout"

    def __init__(self, *, id: int) -> None:
        self.id = id  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Long.read(data)
        
        return Takeout(id=id)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.id))
        
        return data.getvalue()
