from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class BotCommand(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.BotCommand`.

    Details:
        - Layer: ``135``
        - ID: ``-0x3d853739``

    Parameters:
        command: ``str``
        description: ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`bots.GetBotCommands <pyeitaa.raw.functions.bots.GetBotCommands>`
    """

    __slots__: List[str] = ["command", "description"]

    ID = -0x3d853739
    QUALNAME = "types.BotCommand"

    def __init__(self, *, command: str, description: str) -> None:
        self.command = command  # string
        self.description = description  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        command = String.read(data)
        
        description = String.read(data)
        
        return BotCommand(command=command, description=description)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.command))
        
        data.write(String(self.description))
        
        return data.getvalue()
