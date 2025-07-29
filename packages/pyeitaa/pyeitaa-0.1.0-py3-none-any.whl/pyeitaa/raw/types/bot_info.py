from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class BotInfo(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.BotInfo`.

    Details:
        - Layer: ``135``
        - ID: ``0x1b74b335``

    Parameters:
        user_id: ``int`` ``64-bit``
        description: ``str``
        commands: List of :obj:`BotCommand <pyeitaa.raw.base.BotCommand>`
    """

    __slots__: List[str] = ["user_id", "description", "commands"]

    ID = 0x1b74b335
    QUALNAME = "types.BotInfo"

    def __init__(self, *, user_id: int, description: str, commands: List["raw.base.BotCommand"]) -> None:
        self.user_id = user_id  # long
        self.description = description  # string
        self.commands = commands  # Vector<BotCommand>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        user_id = Long.read(data)
        
        description = String.read(data)
        
        commands = TLObject.read(data)
        
        return BotInfo(user_id=user_id, description=description, commands=commands)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.user_id))
        
        data.write(String(self.description))
        
        data.write(Vector(self.commands))
        
        return data.getvalue()
