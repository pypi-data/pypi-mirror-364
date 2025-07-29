from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, Bytes, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class UpdateInlineBotCallbackQuery(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Update`.

    Details:
        - Layer: ``135``
        - ID: ``0x691e9052``

    Parameters:
        query_id: ``int`` ``64-bit``
        user_id: ``int`` ``64-bit``
        msg_id: :obj:`InputBotInlineMessageID <pyeitaa.raw.base.InputBotInlineMessageID>`
        chat_instance: ``int`` ``64-bit``
        data (optional): ``bytes``
        game_short_name (optional): ``str``
    """

    __slots__: List[str] = ["query_id", "user_id", "msg_id", "chat_instance", "data", "game_short_name"]

    ID = 0x691e9052
    QUALNAME = "types.UpdateInlineBotCallbackQuery"

    def __init__(self, *, query_id: int, user_id: int, msg_id: "raw.base.InputBotInlineMessageID", chat_instance: int, data: Optional[bytes] = None, game_short_name: Optional[str] = None) -> None:
        self.query_id = query_id  # long
        self.user_id = user_id  # long
        self.msg_id = msg_id  # InputBotInlineMessageID
        self.chat_instance = chat_instance  # long
        self.data = data  # flags.0?bytes
        self.game_short_name = game_short_name  # flags.1?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        query_id = Long.read(data)
        
        user_id = Long.read(data)
        
        msg_id = TLObject.read(data)
        
        chat_instance = Long.read(data)
        
        data = Bytes.read(data) if flags & (1 << 0) else None
        game_short_name = String.read(data) if flags & (1 << 1) else None
        return UpdateInlineBotCallbackQuery(query_id=query_id, user_id=user_id, msg_id=msg_id, chat_instance=chat_instance, data=data, game_short_name=game_short_name)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.data is not None else 0
        flags |= (1 << 1) if self.game_short_name is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.query_id))
        
        data.write(Long(self.user_id))
        
        data.write(self.msg_id.write())
        
        data.write(Long(self.chat_instance))
        
        if self.data is not None:
            data.write(Bytes(self.data))
        
        if self.game_short_name is not None:
            data.write(String(self.game_short_name))
        
        return data.getvalue()
