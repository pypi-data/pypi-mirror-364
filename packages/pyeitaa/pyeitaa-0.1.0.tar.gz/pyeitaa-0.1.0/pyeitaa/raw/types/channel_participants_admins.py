from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class ChannelParticipantsAdmins(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelParticipantsFilter`.

    Details:
        - Layer: ``135``
        - ID: ``-0x4b9f7697``

    **No parameters required.**
    """

    __slots__: List[str] = []

    ID = -0x4b9f7697
    QUALNAME = "types.ChannelParticipantsAdmins"

    def __init__(self) -> None:
        pass

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        return ChannelParticipantsAdmins()

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        return data.getvalue()
