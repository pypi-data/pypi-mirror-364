from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DataJSON(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.DataJSON`.

    Details:
        - Layer: ``135``
        - ID: ``0x7d748d04``

    Parameters:
        data: ``str``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`bots.SendCustomRequest <pyeitaa.raw.functions.bots.SendCustomRequest>`
            - :obj:`phone.GetCallConfig <pyeitaa.raw.functions.phone.GetCallConfig>`
    """

    __slots__: List[str] = ["data"]

    ID = 0x7d748d04
    QUALNAME = "types.DataJSON"

    def __init__(self, *, data: str) -> None:
        self.data = data  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        data = String.read(data)
        
        return DataJSON(data=data)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.data))
        
        return data.getvalue()
