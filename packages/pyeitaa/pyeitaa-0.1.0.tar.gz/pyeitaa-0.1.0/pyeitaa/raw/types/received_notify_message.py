from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ReceivedNotifyMessage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ReceivedNotifyMessage`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5c7b4887``

    Parameters:
        id: ``int`` ``32-bit``
        flags: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.ReceivedMessages <pyeitaa.raw.functions.messages.ReceivedMessages>`
    """

    __slots__: List[str] = ["id", "flags"]

    ID = -0x5c7b4887
    QUALNAME = "types.ReceivedNotifyMessage"

    def __init__(self, *, id: int, flags: int) -> None:
        self.id = id  # int
        self.flags = flags  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        id = Int.read(data)
        
        flags = Int.read(data)
        
        return ReceivedNotifyMessage(id=id, flags=flags)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.id))
        
        data.write(Int(self.flags))
        
        return data.getvalue()
