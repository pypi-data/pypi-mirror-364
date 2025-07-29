from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class ChatAdminRights(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChatAdminRights`.

    Details:
        - Layer: ``135``
        - ID: ``0x5fb224d5``

    Parameters:
        change_info (optional): ``bool``
        post_messages (optional): ``bool``
        edit_messages (optional): ``bool``
        delete_messages (optional): ``bool``
        ban_users (optional): ``bool``
        invite_users (optional): ``bool``
        pin_messages (optional): ``bool``
        add_admins (optional): ``bool``
        anonymous (optional): ``bool``
        manage_call (optional): ``bool``
        other (optional): ``bool``
        post_live (optional): ``bool``
    """

    __slots__: List[str] = ["change_info", "post_messages", "edit_messages", "delete_messages", "ban_users", "invite_users", "pin_messages", "add_admins", "anonymous", "manage_call", "other", "post_live"]

    ID = 0x5fb224d5
    QUALNAME = "types.ChatAdminRights"

    def __init__(self, *, change_info: Optional[bool] = None, post_messages: Optional[bool] = None, edit_messages: Optional[bool] = None, delete_messages: Optional[bool] = None, ban_users: Optional[bool] = None, invite_users: Optional[bool] = None, pin_messages: Optional[bool] = None, add_admins: Optional[bool] = None, anonymous: Optional[bool] = None, manage_call: Optional[bool] = None, other: Optional[bool] = None, post_live: Optional[bool] = None) -> None:
        self.change_info = change_info  # flags.0?true
        self.post_messages = post_messages  # flags.1?true
        self.edit_messages = edit_messages  # flags.2?true
        self.delete_messages = delete_messages  # flags.3?true
        self.ban_users = ban_users  # flags.4?true
        self.invite_users = invite_users  # flags.5?true
        self.pin_messages = pin_messages  # flags.7?true
        self.add_admins = add_admins  # flags.9?true
        self.anonymous = anonymous  # flags.10?true
        self.manage_call = manage_call  # flags.11?true
        self.other = other  # flags.12?true
        self.post_live = post_live  # flags.20?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        change_info = True if flags & (1 << 0) else False
        post_messages = True if flags & (1 << 1) else False
        edit_messages = True if flags & (1 << 2) else False
        delete_messages = True if flags & (1 << 3) else False
        ban_users = True if flags & (1 << 4) else False
        invite_users = True if flags & (1 << 5) else False
        pin_messages = True if flags & (1 << 7) else False
        add_admins = True if flags & (1 << 9) else False
        anonymous = True if flags & (1 << 10) else False
        manage_call = True if flags & (1 << 11) else False
        other = True if flags & (1 << 12) else False
        post_live = True if flags & (1 << 20) else False
        return ChatAdminRights(change_info=change_info, post_messages=post_messages, edit_messages=edit_messages, delete_messages=delete_messages, ban_users=ban_users, invite_users=invite_users, pin_messages=pin_messages, add_admins=add_admins, anonymous=anonymous, manage_call=manage_call, other=other, post_live=post_live)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.change_info else 0
        flags |= (1 << 1) if self.post_messages else 0
        flags |= (1 << 2) if self.edit_messages else 0
        flags |= (1 << 3) if self.delete_messages else 0
        flags |= (1 << 4) if self.ban_users else 0
        flags |= (1 << 5) if self.invite_users else 0
        flags |= (1 << 7) if self.pin_messages else 0
        flags |= (1 << 9) if self.add_admins else 0
        flags |= (1 << 10) if self.anonymous else 0
        flags |= (1 << 11) if self.manage_call else 0
        flags |= (1 << 12) if self.other else 0
        flags |= (1 << 20) if self.post_live else 0
        data.write(Int(flags))
        
        return data.getvalue()
