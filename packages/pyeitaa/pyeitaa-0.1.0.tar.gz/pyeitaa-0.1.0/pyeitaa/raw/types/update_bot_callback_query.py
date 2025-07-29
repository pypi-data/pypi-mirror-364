from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class UpdateBotCallbackQuery(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``-0x46303b73``

    Parameters:
        query_id: ``int`` ``64-bit``
        user_id: ``int`` ``64-bit``
        peer: :obj:`Peer <pyeitaa.raw.base.Peer>`
        msg_id: ``int`` ``32-bit``
        chat_instance: ``int`` ``64-bit``
        data (optional): ``bytes``
        game_short_name (optional): ``str``
    """

    __slots__: List[str] = ["query_id", "user_id", "peer", "msg_id", "chat_instance", "data", "game_short_name"]

    ID = -0x46303b73
    QUALNAME = "types.UpdateBotCallbackQuery"

    def __init__(self, *, query_id: int, user_id: int, peer: "raw.base.Peer", msg_id: int, chat_instance: int, data: Optional[bytes] = None, game_short_name: Optional[str] = None) -> None:
        self.query_id = query_id  # long
        self.user_id = user_id  # long
        self.peer = peer  # Peer
        self.msg_id = msg_id  # int
        self.chat_instance = chat_instance  # long
        self.data = data  # flags.0?bytes
        self.game_short_name = game_short_name  # flags.1?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        query_id = Long.read(data)
        
        user_id = Long.read(data)
        
        peer = TLObject.read(data)
        
        msg_id = Int.read(data)
        
        chat_instance = Long.read(data)
        
        data = Bytes.read(data) if flags & (1 << 0) else None
        game_short_name = String.read(data) if flags & (1 << 1) else None
        return UpdateBotCallbackQuery(query_id=query_id, user_id=user_id, peer=peer, msg_id=msg_id, chat_instance=chat_instance, data=data, game_short_name=game_short_name)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.data is not None else 0
        flags |= (1 << 1) if self.game_short_name is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.query_id))
        
        data.write(Long(self.user_id))
        
        data.write(self.peer.write())
        
        data.write(Int(self.msg_id))
        
        data.write(Long(self.chat_instance))
        
        if self.data is not None:
            data.write(Bytes(self.data))
        
        if self.game_short_name is not None:
            data.write(String(self.game_short_name))
        
        return data.getvalue()
