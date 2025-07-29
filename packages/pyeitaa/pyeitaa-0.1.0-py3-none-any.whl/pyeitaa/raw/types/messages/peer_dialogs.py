from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class PeerDialogs(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.PeerDialogs`.

    Details:
        - Layer: ``135``
        - ID: ``0x3371c354``

    Parameters:
        dialogs: List of :obj:`Dialog <pyeitaa.raw.base.Dialog>`
        messages: List of :obj:`Message <pyeitaa.raw.base.Message>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`
        state: :obj:`updates.State <pyeitaa.raw.base.updates.State>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetPeerDialogs <pyeitaa.raw.functions.messages.GetPeerDialogs>`
            - :obj:`messages.GetPinnedDialogs <pyeitaa.raw.functions.messages.GetPinnedDialogs>`
    """

    __slots__: List[str] = ["dialogs", "messages", "chats", "users", "state"]

    ID = 0x3371c354
    QUALNAME = "types.messages.PeerDialogs"

    def __init__(self, *, dialogs: List["raw.base.Dialog"], messages: List["raw.base.Message"], chats: List["raw.base.Chat"], users: List["raw.base.User"], state: "raw.base.updates.State") -> None:
        self.dialogs = dialogs  # Vector<Dialog>
        self.messages = messages  # Vector<Message>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>
        self.state = state  # updates.State

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        dialogs = TLObject.read(data)
        
        messages = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        state = TLObject.read(data)
        
        return PeerDialogs(dialogs=dialogs, messages=messages, chats=chats, users=users, state=state)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.dialogs))
        
        data.write(Vector(self.messages))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        data.write(self.state.write())
        
        return data.getvalue()
