from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ImportBotAuthorization(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x67a3ff2c``

    Parameters:
        flags: ``int`` ``32-bit``
        api_id: ``int`` ``32-bit``
        api_hash: ``str``
        bot_auth_token: ``str``

    Returns:
        :obj:`auth.Authorization <pyeitaa.raw.base.auth.Authorization>`
    """

    __slots__: List[str] = ["flags", "api_id", "api_hash", "bot_auth_token"]

    ID = 0x67a3ff2c
    QUALNAME = "functions.auth.ImportBotAuthorization"

    def __init__(self, *, flags: int, api_id: int, api_hash: str, bot_auth_token: str) -> None:
        self.flags = flags  # int
        self.api_id = api_id  # int
        self.api_hash = api_hash  # string
        self.bot_auth_token = bot_auth_token  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        flags = Int.read(data)
        
        api_id = Int.read(data)
        
        api_hash = String.read(data)
        
        bot_auth_token = String.read(data)
        
        return ImportBotAuthorization(flags=flags, api_id=api_id, api_hash=api_hash, bot_auth_token=bot_auth_token)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.flags))
        
        data.write(Int(self.api_id))
        
        data.write(String(self.api_hash))
        
        data.write(String(self.bot_auth_token))
        
        return data.getvalue()
