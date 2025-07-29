from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class GetInactiveChannels(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x11e831ee``

    **No parameters required.**

    Returns:
        :obj:`messages.InactiveChats <pyeitaa.raw.base.messages.InactiveChats>`
    """

    __slots__: List[str] = []

    ID = 0x11e831ee
    QUALNAME = "functions.channels.GetInactiveChannels"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return GetInactiveChannels()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
