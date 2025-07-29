from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ResolveUsername(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x6c3345d``

    Parameters:
        username: ``str``

    Returns:
        :obj:`contacts.ResolvedPeer <pyeitaa.raw.base.contacts.ResolvedPeer>`
    """

    __slots__: List[str] = ["username"]

    ID = -0x6c3345d
    QUALNAME = "functions.contacts.ResolveUsername"

    def __init__(self, *, username: str) -> None:
        self.username = username  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        username = String.read(data)
        
        return ResolveUsername(username=username)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.username))
        
        return data.getvalue()
