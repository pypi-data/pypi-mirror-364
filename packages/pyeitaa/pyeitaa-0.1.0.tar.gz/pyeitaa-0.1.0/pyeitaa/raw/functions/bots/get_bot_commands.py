from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetBotCommands(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x1cb3f22a``

    Parameters:
        scope: :obj:`BotCommandScope <pyeitaa.raw.base.BotCommandScope>`
        lang_code: ``str``

    Returns:
        List of :obj:`BotCommand <pyeitaa.raw.base.BotCommand>`
    """

    __slots__: List[str] = ["scope", "lang_code"]

    ID = -0x1cb3f22a
    QUALNAME = "functions.bots.GetBotCommands"

    def __init__(self, *, scope: "raw.base.BotCommandScope", lang_code: str) -> None:
        self.scope = scope  # BotCommandScope
        self.lang_code = lang_code  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        scope = TLObject.read(data)
        
        lang_code = String.read(data)
        
        return GetBotCommands(scope=scope, lang_code=lang_code)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.scope.write())
        
        data.write(String(self.lang_code))
        
        return data.getvalue()
