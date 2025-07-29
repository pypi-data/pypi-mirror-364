from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class KeyboardButtonRow(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.KeyboardButtonRow`.

    Details:
        - Layer: ``135``
        - ID: ``0x77608b83``

    Parameters:
        buttons: List of :obj:`KeyboardButton <pyeitaa.raw.base.KeyboardButton>`
    """

    __slots__: List[str] = ["buttons"]

    ID = 0x77608b83
    QUALNAME = "types.KeyboardButtonRow"

    def __init__(self, *, buttons: List["raw.base.KeyboardButton"]) -> None:
        self.buttons = buttons  # Vector<KeyboardButton>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        buttons = TLObject.read(data)
        
        return KeyboardButtonRow(buttons=buttons)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.buttons))
        
        return data.getvalue()
