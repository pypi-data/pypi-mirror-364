from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class UpdateBotCommands(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x4d712f2e``

    Parameters:
        peer: :obj:`Peer <pyeitaa.raw.base.Peer>`
        bot_id: ``int`` ``64-bit``
        commands: List of :obj:`BotCommand <pyeitaa.raw.base.BotCommand>`
    """

    __slots__: List[str] = ["peer", "bot_id", "commands"]

    ID = 0x4d712f2e
    QUALNAME = "types.UpdateBotCommands"

    def __init__(self, *, peer: "raw.base.Peer", bot_id: int, commands: List["raw.base.BotCommand"]) -> None:
        self.peer = peer  # Peer
        self.bot_id = bot_id  # long
        self.commands = commands  # Vector<BotCommand>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        peer = TLObject.read(data)
        
        bot_id = Long.read(data)
        
        commands = TLObject.read(data)
        
        return UpdateBotCommands(peer=peer, bot_id=bot_id, commands=commands)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.peer.write())
        
        data.write(Long(self.bot_id))
        
        data.write(Vector(self.commands))
        
        return data.getvalue()
