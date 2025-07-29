from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ChannelParticipantsNotModified(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.channels.ChannelParticipants`.

    Details:
        - Layer: ``135``
        - ID: ``-0xfe8c017``

    **No parameters required.**

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`channels.GetParticipants <pyeitaa.raw.functions.channels.GetParticipants>`
    """

    __slots__: List[str] = []

    ID = -0xfe8c017
    QUALNAME = "types.channels.ChannelParticipantsNotModified"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return ChannelParticipantsNotModified()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
