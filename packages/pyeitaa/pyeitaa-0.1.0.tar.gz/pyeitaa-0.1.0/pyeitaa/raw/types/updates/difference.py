from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class Difference(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.updates.Difference`.

    Details:
        - Layer: ``135``
        - ID: ``0xf49ca0``

    Parameters:
        new_messages: List of :obj:`Message <pyeitaa.raw.base.Message>`
        new_encrypted_messages: List of :obj:`EncryptedMessage <pyeitaa.raw.base.EncryptedMessage>`
        other_updates: List of :obj:`Update <pyeitaa.raw.base.Update>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`
        state: :obj:`updates.State <pyeitaa.raw.base.updates.State>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`updates.GetDifference <pyeitaa.raw.functions.updates.GetDifference>`
    """

    __slots__: List[str] = ["new_messages", "new_encrypted_messages", "other_updates", "chats", "users", "state"]

    ID = 0xf49ca0
    QUALNAME = "types.updates.Difference"

    def __init__(self, *, new_messages: List["raw.base.Message"], new_encrypted_messages: List["raw.base.EncryptedMessage"], other_updates: List["raw.base.Update"], chats: List["raw.base.Chat"], users: List["raw.base.User"], state: "raw.base.updates.State") -> None:
        self.new_messages = new_messages  # Vector<Message>
        self.new_encrypted_messages = new_encrypted_messages  # Vector<EncryptedMessage>
        self.other_updates = other_updates  # Vector<Update>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>
        self.state = state  # updates.State

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        new_messages = TLObject.read(data)
        
        new_encrypted_messages = TLObject.read(data)
        
        other_updates = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        state = TLObject.read(data)
        
        return Difference(new_messages=new_messages, new_encrypted_messages=new_encrypted_messages, other_updates=other_updates, chats=chats, users=users, state=state)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.new_messages))
        
        data.write(Vector(self.new_encrypted_messages))
        
        data.write(Vector(self.other_updates))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        data.write(self.state.write())
        
        return data.getvalue()
