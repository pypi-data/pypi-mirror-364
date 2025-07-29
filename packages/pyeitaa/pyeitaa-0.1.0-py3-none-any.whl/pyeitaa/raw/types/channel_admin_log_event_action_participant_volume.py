from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChannelAdminLogEventActionParticipantVolume(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``135``
        - ID: ``0x3e7f6847``

    Parameters:
        participant: :obj:`GroupCallParticipant <pyeitaa.raw.base.GroupCallParticipant>`
    """

    __slots__: List[str] = ["participant"]

    ID = 0x3e7f6847
    QUALNAME = "types.ChannelAdminLogEventActionParticipantVolume"

    def __init__(self, *, participant: "raw.base.GroupCallParticipant") -> None:
        self.participant = participant  # GroupCallParticipant

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        participant = TLObject.read(data)
        
        return ChannelAdminLogEventActionParticipantVolume(participant=participant)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.participant.write())
        
        return data.getvalue()
