from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class InlineQueryPeerTypeSameBotPM(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.InlineQueryPeerType`.

    Details:
        - Layer: ``135``
        - ID: ``0x3081ed9d``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = 0x3081ed9d
    QUALNAME = "types.InlineQueryPeerTypeSameBotPM"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return InlineQueryPeerTypeSameBotPM()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
