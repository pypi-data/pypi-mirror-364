from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChannelAdminLogEventActionParticipantInvite(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1ce3cb28``

    Parameters:
        participant: :obj:`ChannelParticipant <pyeitaa.raw.base.ChannelParticipant>`
    """

    __slots__: List[str] = ["participant"]

    ID = -0x1ce3cb28
    QUALNAME = "types.ChannelAdminLogEventActionParticipantInvite"

    def __init__(self, *, participant: "raw.base.ChannelParticipant") -> None:
        self.participant = participant  # ChannelParticipant

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        participant = TLObject.read(data)
        
        return ChannelAdminLogEventActionParticipantInvite(participant=participant)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.participant.write())
        
        return data.getvalue()
