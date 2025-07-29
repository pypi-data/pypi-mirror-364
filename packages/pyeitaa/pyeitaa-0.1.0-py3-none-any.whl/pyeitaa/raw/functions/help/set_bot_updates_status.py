from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class SetBotUpdatesStatus(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x13dd3033``

    Parameters:
        pending_updates_count: ``int`` ``32-bit``
        message: ``str``

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["pending_updates_count", "message"]

    ID = -0x13dd3033
    QUALNAME = "functions.help.SetBotUpdatesStatus"

    def __init__(self, *, pending_updates_count: int, message: str) -> None:
        self.pending_updates_count = pending_updates_count  # int
        self.message = message  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        pending_updates_count = Int.read(data)
        
        message = String.read(data)
        
        return SetBotUpdatesStatus(pending_updates_count=pending_updates_count, message=message)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.pending_updates_count))
        
        data.write(String(self.message))
        
        return data.getvalue()
