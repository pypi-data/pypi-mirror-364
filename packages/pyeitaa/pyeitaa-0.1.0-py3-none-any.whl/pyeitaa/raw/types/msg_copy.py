from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class MsgCopy(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageCopy`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1f9fb94e``

    Parameters:
        orig_message: :obj:`Message <pyeitaa.raw.base.Message>`
    """

    __slots__: List[str] = ["orig_message"]

    ID = -0x1f9fb94e
    QUALNAME = "types.MsgCopy"

    def __init__(self, *, orig_message: "raw.base.Message") -> None:
        self.orig_message = orig_message  # Message

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        orig_message = TLObject.read(data)
        
        return MsgCopy(orig_message=orig_message)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.orig_message.write())
        
        return data.getvalue()
