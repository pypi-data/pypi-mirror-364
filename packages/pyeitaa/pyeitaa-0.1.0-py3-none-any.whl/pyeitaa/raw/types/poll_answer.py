from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class PollAnswer(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.PollAnswer`.

    Details:
        - Layer: ``135``
        - ID: ``0x6ca9c2e9``

    Parameters:
        text: ``str``
        option: ``bytes``
    """

    __slots__: List[str] = ["text", "option"]

    ID = 0x6ca9c2e9
    QUALNAME = "types.PollAnswer"

    def __init__(self, *, text: str, option: bytes) -> None:
        self.text = text  # string
        self.option = option  # bytes

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        text = String.read(data)
        
        option = Bytes.read(data)
        
        return PollAnswer(text=text, option=option)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.text))
        
        data.write(Bytes(self.option))
        
        return data.getvalue()
