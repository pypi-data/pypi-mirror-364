from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class EditBanned(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x6919327f``

    Parameters:
        channel: :obj:`InputChannel <pyeitaa.raw.base.InputChannel>`
        participant: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        banned_rights: :obj:`ChatBannedRights <pyeitaa.raw.base.ChatBannedRights>`

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["channel", "participant", "banned_rights"]

    ID = -0x6919327f
    QUALNAME = "functions.channels.EditBanned"

    def __init__(self, *, channel: "raw.base.InputChannel", participant: "raw.base.InputPeer", banned_rights: "raw.base.ChatBannedRights") -> None:
        self.channel = channel  # InputChannel
        self.participant = participant  # InputPeer
        self.banned_rights = banned_rights  # ChatBannedRights

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        channel = TLObject.read(data)
        
        participant = TLObject.read(data)
        
        banned_rights = TLObject.read(data)
        
        return EditBanned(channel=channel, participant=participant, banned_rights=banned_rights)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.channel.write())
        
        data.write(self.participant.write())
        
        data.write(self.banned_rights.write())
        
        return data.getvalue()
