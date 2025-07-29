from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageActionCustomAction(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x51960aa``

    Parameters:
        message: ``str``
    """

    __slots__: List[str] = ["message"]

    ID = -0x51960aa
    QUALNAME = "types.MessageActionCustomAction"

    def __init__(self, *, message: str) -> None:
        self.message = message  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        message = String.read(data)
        
        return MessageActionCustomAction(message=message)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.message))
        
        return data.getvalue()
