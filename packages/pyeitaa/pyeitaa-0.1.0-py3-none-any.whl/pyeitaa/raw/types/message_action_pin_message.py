from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class MessageActionPinMessage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x6b42c713``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = -0x6b42c713
    QUALNAME = "types.MessageActionPinMessage"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return MessageActionPinMessage()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
