from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class ChatInviteAlready(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChatInvite`.

    Details:
        - Layer: ``135``
        - ID: ``0x5a686d7c``

    Parameters:
        chat: :obj:`Chat <pyeitaa.raw.base.Chat>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.CheckChatInvite <pyeitaa.raw.functions.messages.CheckChatInvite>`
    """

    __slots__: List[str] = ["chat"]

    ID = 0x5a686d7c
    QUALNAME = "types.ChatInviteAlready"

    def __init__(self, *, chat: "raw.base.Chat") -> None:
        self.chat = chat  # Chat

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        chat = TLObject.read(data)
        
        return ChatInviteAlready(chat=chat)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(self.chat.write())
        
        return data.getvalue()
