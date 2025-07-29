from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChannelAdminLogEventActionParticipantToggleBan(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1927c282``

    Parameters:
        prev_participant: :obj:`ChannelParticipant <pyeitaa.raw.base.ChannelParticipant>`
        new_participant: :obj:`ChannelParticipant <pyeitaa.raw.base.ChannelParticipant>`
    """

    __slots__: List[str] = ["prev_participant", "new_participant"]

    ID = -0x1927c282
    QUALNAME = "types.ChannelAdminLogEventActionParticipantToggleBan"

    def __init__(self, *, prev_participant: "raw.base.ChannelParticipant", new_participant: "raw.base.ChannelParticipant") -> None:
        self.prev_participant = prev_participant  # ChannelParticipant
        self.new_participant = new_participant  # ChannelParticipant

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        prev_participant = TLObject.read(data)
        
        new_participant = TLObject.read(data)
        
        return ChannelAdminLogEventActionParticipantToggleBan(prev_participant=prev_participant, new_participant=new_participant)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.prev_participant.write())
        
        data.write(self.new_participant.write())
        
        return data.getvalue()
