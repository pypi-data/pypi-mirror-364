from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InputGameShortName(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InputGame`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3cce17f6``

    Parameters:
        bot_id: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        short_name: ``str``
    """

    __slots__: List[str] = ["bot_id", "short_name"]

    ID = -0x3cce17f6
    QUALNAME = "types.InputGameShortName"

    def __init__(self, *, bot_id: "raw.base.InputUser", short_name: str) -> None:
        self.bot_id = bot_id  # InputUser
        self.short_name = short_name  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        bot_id = TLObject.read(data)
        
        short_name = String.read(data)
        
        return InputGameShortName(bot_id=bot_id, short_name=short_name)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.bot_id.write())
        
        data.write(String(self.short_name))
        
        return data.getvalue()
