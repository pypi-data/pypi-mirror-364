from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetAuthorizationForm(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x56d6a686``

    Parameters:
        bot_id: ``int`` ``64-bit``
        scope: ``str``
        public_key: ``str``

    Returns:
        :obj:`account.AuthorizationForm <pyeitaa.raw.base.account.AuthorizationForm>`
    """

    __slots__: List[str] = ["bot_id", "scope", "public_key"]

    ID = -0x56d6a686
    QUALNAME = "functions.account.GetAuthorizationForm"

    def __init__(self, *, bot_id: int, scope: str, public_key: str) -> None:
        self.bot_id = bot_id  # long
        self.scope = scope  # string
        self.public_key = public_key  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        bot_id = Long.read(data)
        
        scope = String.read(data)
        
        public_key = String.read(data)
        
        return GetAuthorizationForm(bot_id=bot_id, scope=scope, public_key=public_key)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.bot_id))
        
        data.write(String(self.scope))
        
        data.write(String(self.public_key))
        
        return data.getvalue()
