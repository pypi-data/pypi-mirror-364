from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetParticipant(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x5f54933a``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        participant: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`

    Returns:
        :obj:`channels.ChannelParticipant <pyeitaa.raw.base.channels.ChannelParticipant>`
    """

    __slots__: List[str] = ["channel", "participant"]

    ID = -0x5f54933a
    QUALNAME = "functions.channels.GetParticipant"

    def __init__(self, *, channel: "raw.base.InputChannel", participant: "raw.base.InputPeer") -> None:
        self.channel = channel  # InputChannel
        self.participant = participant  # InputPeer

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        participant = TLObject.read(data)
        
        return GetParticipant(channel=channel, participant=participant)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(self.participant.write())
        
        return data.getvalue()
