from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InputMessagesFilterRoundVideo(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.MessagesFilter`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4ab625ad``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = -0x4ab625ad
    QUALNAME = "types.InputMessagesFilterRoundVideo"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return InputMessagesFilterRoundVideo()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
