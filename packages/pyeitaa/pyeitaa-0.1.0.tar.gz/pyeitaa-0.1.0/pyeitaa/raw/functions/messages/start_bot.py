from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class StartBot(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x19208c88``

    Parameters:
        bot: :obj:`InputUser <pyeitaa.raw.base.InputUser>`
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        random_id: ``int`` ``64-bit``
        start_param: ``str``

    Returns:
        :obj:`Updates <pyeitaa.raw.base.Updates>`
    """

    __slots__: List[str] = ["bot", "peer", "random_id", "start_param"]

    ID = -0x19208c88
    QUALNAME = "functions.messages.StartBot"

    def __init__(self, *, bot: "raw.base.InputUser", peer: "raw.base.InputPeer", random_id: int, start_param: str) -> None:
        self.bot = bot  # InputUser
        self.peer = peer  # InputPeer
        self.random_id = random_id  # long
        self.start_param = start_param  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        bot = TLObject.read(data)
        
        peer = TLObject.read(data)
        
        random_id = Long.read(data)
        
        start_param = String.read(data)
        
        return StartBot(bot=bot, peer=peer, random_id=random_id, start_param=start_param)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.bot.write())
        
        data.write(self.peer.write())
        
        data.write(Long(self.random_id))
        
        data.write(String(self.start_param))
        
        return data.getvalue()
