from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ChannelParticipantsBanned(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelParticipantsFilter`.

    Details:
        - Layer: ``135``
        - ID: ``0x1427a5e1``

    Parameters:
        q: ``str``
    """

    __slots__: List[str] = ["q"]

    ID = 0x1427a5e1
    QUALNAME = "types.ChannelParticipantsBanned"

    def __init__(self, *, q: str) -> None:
        self.q = q  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        q = String.read(data)
        
        return ChannelParticipantsBanned(q=q)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(String(self.q))
        
        return data.getvalue()
