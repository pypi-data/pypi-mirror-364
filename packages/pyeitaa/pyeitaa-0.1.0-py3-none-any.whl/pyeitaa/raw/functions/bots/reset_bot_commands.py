from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ResetBotCommands(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x3d8de0f9``

    Parameters:
        scope: :obj:`BotCommandScope <pyeitaa.raw.base.BotCommandScope>`
        lang_code: ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["scope", "lang_code"]

    ID = 0x3d8de0f9
    QUALNAME = "functions.bots.ResetBotCommands"

    def __init__(self, *, scope: "raw.base.BotCommandScope", lang_code: str) -> None:
        self.scope = scope  # BotCommandScope
        self.lang_code = lang_code  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        scope = TLObject.read(data)
        
        lang_code = String.read(data)
        
        return ResetBotCommands(scope=scope, lang_code=lang_code)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.scope.write())
        
        data.write(String(self.lang_code))
        
        return data.getvalue()
