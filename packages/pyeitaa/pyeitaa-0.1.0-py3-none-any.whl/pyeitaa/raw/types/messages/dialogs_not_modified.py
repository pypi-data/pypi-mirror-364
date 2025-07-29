from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class DialogsNotModified(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.Dialogs`.

    Details:
        - Layer: ``135``
        - ID: ``-0xf1c1a6a``

    Parameters:
        count: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetDialogs <pyeitaa.raw.functions.messages.GetDialogs>`
    """

    __slots__: List[str] = ["count"]

    ID = -0xf1c1a6a
    QUALNAME = "types.messages.DialogsNotModified"

    def __init__(self, *, count: int) -> None:
        self.count = count  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        count = Int.read(data)
        
        return DialogsNotModified(count=count)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.count))
        
        return data.getvalue()
