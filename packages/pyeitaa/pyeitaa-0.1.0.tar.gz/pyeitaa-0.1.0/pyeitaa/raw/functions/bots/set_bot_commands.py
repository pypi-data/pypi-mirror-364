from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class SetBotCommands(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x517165a``

    Parameters:
        scope: :obj:`BotCommandScope <pyeitaa.raw.base.BotCommandScope>`
        lang_code: ``str``
        commands: List of :obj:`BotCommand <pyeitaa.raw.base.BotCommand>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["scope", "lang_code", "commands"]

    ID = 0x517165a
    QUALNAME = "functions.bots.SetBotCommands"

    def __init__(self, *, scope: "raw.base.BotCommandScope", lang_code: str, commands: List["raw.base.BotCommand"]) -> None:
        self.scope = scope  # BotCommandScope
        self.lang_code = lang_code  # string
        self.commands = commands  # Vector<BotCommand>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        scope = TLObject.read(data)
        
        lang_code = String.read(data)
        
        commands = TLObject.read(data)
        
        return SetBotCommands(scope=scope, lang_code=lang_code, commands=commands)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.scope.write())
        
        data.write(String(self.lang_code))
        
        data.write(Vector(self.commands))
        
        return data.getvalue()
