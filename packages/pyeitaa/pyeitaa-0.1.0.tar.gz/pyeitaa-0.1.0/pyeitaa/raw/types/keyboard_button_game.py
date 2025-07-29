from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class KeyboardButtonGame(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.KeyboardButton`.

    Details:
        - Layer: ``135``
        - ID: ``0x50f41ccf``

    Parameters:
        text: ``str``
    """

    __slots__: List[str] = ["text"]

    ID = 0x50f41ccf
    QUALNAME = "types.KeyboardButtonGame"

    def __init__(self, *, text: str) -> None:
        self.text = text  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        text = String.read(data)
        
        return KeyboardButtonGame(text=text)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.text))
        
        return data.getvalue()
