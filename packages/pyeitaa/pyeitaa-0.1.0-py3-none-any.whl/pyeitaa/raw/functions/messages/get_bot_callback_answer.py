from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Bytes
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class GetBotCallbackAnswer(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x6cbd35f9``

    Parameters:
        peer: :obj:`InputPeer <pyeitaa.raw.base.InputPeer>`
        msg_id: ``int`` ``32-bit``
        game (optional): ``bool``
        data (optional): ``bytes``
        password (optional): :obj:`InputCheckPasswordSRP <pyeitaa.raw.base.InputCheckPasswordSRP>`

    Returns:
        :obj:`messages.BotCallbackAnswer <pyeitaa.raw.base.messages.BotCallbackAnswer>`
    """

    __slots__: List[str] = ["peer", "msg_id", "game", "data", "password"]

    ID = -0x6cbd35f9
    QUALNAME = "functions.messages.GetBotCallbackAnswer"

    def __init__(self, *, peer: "raw.base.InputPeer", msg_id: int, game: Optional[bool] = None, data: Optional[bytes] = None, password: "raw.base.InputCheckPasswordSRP" = None) -> None:
        self.peer = peer  # InputPeer
        self.msg_id = msg_id  # int
        self.game = game  # flags.1?true
        self.data = data  # flags.0?bytes
        self.password = password  # flags.2?InputCheckPasswordSRP

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        game = True if flags & (1 << 1) else False
        peer = TLObject.read(data)
        
        msg_id = Int.read(data)
        
        data = Bytes.read(data) if flags & (1 << 0) else None
        password = TLObject.read(data) if flags & (1 << 2) else None
        
        return GetBotCallbackAnswer(peer=peer, msg_id=msg_id, game=game, data=data, password=password)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.game else 0
        flags |= (1 << 0) if self.data is not None else 0
        flags |= (1 << 2) if self.password is not None else 0
        data.write(Int(flags))
        
        data.write(self.peer.write())
        
        data.write(Int(self.msg_id))
        
        if self.data is not None:
            data.write(Bytes(self.data))
        
        if self.password is not None:
            data.write(self.password.write())
        
        return data.getvalue()
