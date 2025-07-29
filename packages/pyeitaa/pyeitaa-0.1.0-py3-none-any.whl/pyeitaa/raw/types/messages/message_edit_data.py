from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class MessageEditData(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.MessageEditData`.

    Details:
        - Layer: ``135``
        - ID: ``0x26b5dde6``

    Parameters:
        caption (optional): ``bool``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetMessageEditData <pyeitaa.raw.functions.messages.GetMessageEditData>`
    """

    __slots__: List[str] = ["caption"]

    ID = 0x26b5dde6
    QUALNAME = "types.messages.MessageEditData"

    def __init__(self, *, caption: Optional[bool] = None) -> None:
        self.caption = caption  # flags.0?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        caption = True if flags & (1 << 0) else False
        return MessageEditData(caption=caption)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.caption else 0
        data.write(Int(flags))
        
        return data.getvalue()
