from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SendMessageTypingAction(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.SendMessageAction`.

    Details:
        - Layer: ``135``
        - ID: ``0x16bf744e``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = 0x16bf744e
    QUALNAME = "types.SendMessageTypingAction"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return SendMessageTypingAction()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
