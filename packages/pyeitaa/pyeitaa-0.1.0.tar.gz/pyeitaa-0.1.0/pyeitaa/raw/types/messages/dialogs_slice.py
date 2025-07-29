from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class DialogsSlice(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.messages.Dialogs`.

    Details:
        - Layer: ``135``
        - ID: ``0x71e094f3``

    Parameters:
        count: ``int`` ``32-bit``
        dialogs: List of :obj:`Dialog <pyeitaa.raw.base.Dialog>`
        messages: List of :obj:`Message <pyeitaa.raw.base.Message>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetDialogs <pyeitaa.raw.functions.messages.GetDialogs>`
    """

    __slots__: List[str] = ["count", "dialogs", "messages", "chats", "users"]

    ID = 0x71e094f3
    QUALNAME = "types.messages.DialogsSlice"

    def __init__(self, *, count: int, dialogs: List["raw.base.Dialog"], messages: List["raw.base.Message"], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.count = count  # int
        self.dialogs = dialogs  # Vector<Dialog>
        self.messages = messages  # Vector<Message>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        count = Int.read(data)
        
        dialogs = TLObject.read(data)
        
        messages = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return DialogsSlice(count=count, dialogs=dialogs, messages=messages, chats=chats, users=users)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.count))
        
        data.write(Vector(self.dialogs))
        
        data.write(Vector(self.messages))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()
