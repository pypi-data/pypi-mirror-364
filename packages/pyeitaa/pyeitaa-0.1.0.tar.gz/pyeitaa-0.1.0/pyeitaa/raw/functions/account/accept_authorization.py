from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class AcceptAuthorization(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0xc12b38d``

    Parameters:
        bot_id: ``int`` ``64-bit``
        scope: ``str``
        public_key: ``str``
        value_hashes: List of :obj:`SecureValueHash <pyeitaa.raw.base.SecureValueHash>`
        credentials: :obj:`SecureCredentialsEncrypted <pyeitaa.raw.base.SecureCredentialsEncrypted>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["bot_id", "scope", "public_key", "value_hashes", "credentials"]

    ID = -0xc12b38d
    QUALNAME = "functions.account.AcceptAuthorization"

    def __init__(self, *, bot_id: int, scope: str, public_key: str, value_hashes: List["raw.base.SecureValueHash"], credentials: "raw.base.SecureCredentialsEncrypted") -> None:
        self.bot_id = bot_id  # long
        self.scope = scope  # string
        self.public_key = public_key  # string
        self.value_hashes = value_hashes  # Vector<SecureValueHash>
        self.credentials = credentials  # SecureCredentialsEncrypted

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        bot_id = Long.read(data)
        
        scope = String.read(data)
        
        public_key = String.read(data)
        
        value_hashes = TLObject.read(data)
        
        credentials = TLObject.read(data)
        
        return AcceptAuthorization(bot_id=bot_id, scope=scope, public_key=public_key, value_hashes=value_hashes, credentials=credentials)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Long(self.bot_id))
        
        data.write(String(self.scope))
        
        data.write(String(self.public_key))
        
        data.write(Vector(self.value_hashes))
        
        data.write(self.credentials.write())
        
        return data.getvalue()
