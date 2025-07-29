from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChatInvitePeek(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChatInvite`.

    Details:
        - Layer: ``135``
        - ID: ``0x61695cb0``

    Parameters:
        chat: :obj:`Chat <pyeitaa.raw.base.Chat>`
        expires: ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.CheckChatInvite <pyeitaa.raw.functions.messages.CheckChatInvite>`
    """

    __slots__: List[str] = ["chat", "expires"]

    ID = 0x61695cb0
    QUALNAME = "types.ChatInvitePeek"

    def __init__(self, *, chat: "raw.base.Chat", expires: int) -> None:
        self.chat = chat  # Chat
        self.expires = expires  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        chat = TLObject.read(data)
        
        expires = Int.read(data)
        
        return ChatInvitePeek(chat=chat, expires=expires)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.chat.write())
        
        data.write(Int(self.expires))
        
        return data.getvalue()
