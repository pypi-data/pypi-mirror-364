from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ChannelDifferenceTooLong(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.updates.ChannelDifference`.

    Details:
        - Layer: ``135``
        - ID: ``-0x5b433902``

    Parameters:
        dialog: :obj:`Dialog <pyeitaa.raw.base.Dialog>`
        messages: List of :obj:`Message <pyeitaa.raw.base.Message>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`
        final (optional): ``bool``
        timeout (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`updates.GetChannelDifference <pyeitaa.raw.functions.updates.GetChannelDifference>`
    """

    __slots__: List[str] = ["dialog", "messages", "chats", "users", "final", "timeout"]

    ID = -0x5b433902
    QUALNAME = "types.updates.ChannelDifferenceTooLong"

    def __init__(self, *, dialog: "raw.base.Dialog", messages: List["raw.base.Message"], chats: List["raw.base.Chat"], users: List["raw.base.User"], final: Optional[bool] = None, timeout: Optional[int] = None) -> None:
        self.dialog = dialog  # Dialog
        self.messages = messages  # Vector<Message>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>
        self.final = final  # flags.0?true
        self.timeout = timeout  # flags.1?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        final = True if flags & (1 << 0) else False
        timeout = Int.read(data) if flags & (1 << 1) else None
        dialog = TLObject.read(data)
        
        messages = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        users = TLObject.read(data)
        
        return ChannelDifferenceTooLong(dialog=dialog, messages=messages, chats=chats, users=users, final=final, timeout=timeout)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.final else 0
        flags |= (1 << 1) if self.timeout is not None else 0
        data.write(Int(flags))
        
        if self.timeout is not None:
            data.write(Int(self.timeout))
        
        data.write(self.dialog.write())
        
        data.write(Vector(self.messages))
        
        data.write(Vector(self.chats))
        
        data.write(Vector(self.users))
        
        return data.getvalue()
