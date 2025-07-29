from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class GetParticipants(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``0x77ced9d0``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        filter: :obj:`ChannelParticipantsFilter <pyeitaa.raw.base.ChannelParticipantsFilter>`
        offset: ``int`` ``32-bit``
        limit: ``int`` ``32-bit``
        hash: ``int`` ``64-bit``

    Returns:
        :obj:`channels.ChannelParticipants <pyeitaa.raw.base.channels.ChannelParticipants>`
    """

    __slots__: List[str] = ["channel", "filter", "offset", "limit", "hash"]

    ID = 0x77ced9d0
    QUALNAME = "functions.channels.GetParticipants"

    def __init__(self, *, channel: "raw.base.InputChannel", filter: "raw.base.ChannelParticipantsFilter", offset: int, limit: int, hash: int) -> None:
        self.channel = channel  # InputChannel
        self.filter = filter  # ChannelParticipantsFilter
        self.offset = offset  # int
        self.limit = limit  # int
        self.hash = hash  # long

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        filter = TLObject.read(data)
        
        offset = Int.read(data)
        
        limit = Int.read(data)
        
        hash = Long.read(data)
        
        return GetParticipants(channel=channel, filter=filter, offset=offset, limit=limit, hash=hash)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(self.filter.write())
        
        data.write(Int(self.offset))
        
        data.write(Int(self.limit))
        
        data.write(Long(self.hash))
        
        return data.getvalue()
