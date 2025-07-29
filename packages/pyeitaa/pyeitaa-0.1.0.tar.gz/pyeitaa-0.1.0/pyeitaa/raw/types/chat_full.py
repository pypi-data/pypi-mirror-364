from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ChatFull(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChatFull`.

    Details:
        - Layer: ``135``
        - ID: ``0x4dbdc099``

    Parameters:
        id: ``int`` ``64-bit``
        about: ``str``
        participants: :obj:`ChatParticipants <pyeitaa.raw.base.ChatParticipants>`
        notify_settings: :obj:`PeerNotifySettings <pyeitaa.raw.base.PeerNotifySettings>`
        can_set_username (optional): ``bool``
        has_scheduled (optional): ``bool``
        chat_photo (optional): :obj:`Photo <pyeitaa.raw.base.Photo>`
        exported_invite (optional): :obj:`ExportedChatInvite <pyeitaa.raw.base.ExportedChatInvite>`
        bot_info (optional): List of :obj:`BotInfo <pyeitaa.raw.base.BotInfo>`
        pinned_msg_id (optional): ``int`` ``32-bit``
        folder_id (optional): ``int`` ``32-bit``
        call (optional): :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`
        ttl_period (optional): ``int`` ``32-bit``
        groupcall_default_join_as (optional): :obj:`Peer <pyeitaa.raw.base.Peer>`
        theme_emoticon (optional): ``str``
    """

    __slots__: List[str] = ["id", "about", "participants", "notify_settings", "can_set_username", "has_scheduled", "chat_photo", "exported_invite", "bot_info", "pinned_msg_id", "folder_id", "call", "ttl_period", "groupcall_default_join_as", "theme_emoticon"]

    ID = 0x4dbdc099
    QUALNAME = "types.ChatFull"

    def __init__(self, *, id: int, about: str, participants: "raw.base.ChatParticipants", notify_settings: "raw.base.PeerNotifySettings", can_set_username: Optional[bool] = None, has_scheduled: Optional[bool] = None, chat_photo: "raw.base.Photo" = None, exported_invite: "raw.base.ExportedChatInvite" = None, bot_info: Optional[List["raw.base.BotInfo"]] = None, pinned_msg_id: Optional[int] = None, folder_id: Optional[int] = None, call: "raw.base.InputGroupCall" = None, ttl_period: Optional[int] = None, groupcall_default_join_as: "raw.base.Peer" = None, theme_emoticon: Optional[str] = None) -> None:
        self.id = id  # long
        self.about = about  # string
        self.participants = participants  # ChatParticipants
        self.notify_settings = notify_settings  # PeerNotifySettings
        self.can_set_username = can_set_username  # flags.7?true
        self.has_scheduled = has_scheduled  # flags.8?true
        self.chat_photo = chat_photo  # flags.2?Photo
        self.exported_invite = exported_invite  # flags.13?ExportedChatInvite
        self.bot_info = bot_info  # flags.3?Vector<BotInfo>
        self.pinned_msg_id = pinned_msg_id  # flags.6?int
        self.folder_id = folder_id  # flags.11?int
        self.call = call  # flags.12?InputGroupCall
        self.ttl_period = ttl_period  # flags.14?int
        self.groupcall_default_join_as = groupcall_default_join_as  # flags.15?Peer
        self.theme_emoticon = theme_emoticon  # flags.16?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        can_set_username = True if flags & (1 << 7) else False
        has_scheduled = True if flags & (1 << 8) else False
        id = Long.read(data)
        
        about = String.read(data)
        
        participants = TLObject.read(data)
        
        chat_photo = TLObject.read(data) if flags & (1 << 2) else None
        
        notify_settings = TLObject.read(data)
        
        exported_invite = TLObject.read(data) if flags & (1 << 13) else None
        
        bot_info = TLObject.read(data) if flags & (1 << 3) else []
        
        pinned_msg_id = Int.read(data) if flags & (1 << 6) else None
        folder_id = Int.read(data) if flags & (1 << 11) else None
        call = TLObject.read(data) if flags & (1 << 12) else None
        
        ttl_period = Int.read(data) if flags & (1 << 14) else None
        groupcall_default_join_as = TLObject.read(data) if flags & (1 << 15) else None
        
        theme_emoticon = String.read(data) if flags & (1 << 16) else None
        return ChatFull(id=id, about=about, participants=participants, notify_settings=notify_settings, can_set_username=can_set_username, has_scheduled=has_scheduled, chat_photo=chat_photo, exported_invite=exported_invite, bot_info=bot_info, pinned_msg_id=pinned_msg_id, folder_id=folder_id, call=call, ttl_period=ttl_period, groupcall_default_join_as=groupcall_default_join_as, theme_emoticon=theme_emoticon)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 7) if self.can_set_username else 0
        flags |= (1 << 8) if self.has_scheduled else 0
        flags |= (1 << 2) if self.chat_photo is not None else 0
        flags |= (1 << 13) if self.exported_invite is not None else 0
        flags |= (1 << 3) if self.bot_info is not None else 0
        flags |= (1 << 6) if self.pinned_msg_id is not None else 0
        flags |= (1 << 11) if self.folder_id is not None else 0
        flags |= (1 << 12) if self.call is not None else 0
        flags |= (1 << 14) if self.ttl_period is not None else 0
        flags |= (1 << 15) if self.groupcall_default_join_as is not None else 0
        flags |= (1 << 16) if self.theme_emoticon is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.id))
        
        data.write(String(self.about))
        
        data.write(self.participants.write())
        
        if self.chat_photo is not None:
            data.write(self.chat_photo.write())
        
        data.write(self.notify_settings.write())
        
        if self.exported_invite is not None:
            data.write(self.exported_invite.write())
        
        if self.bot_info is not None:
            data.write(Vector(self.bot_info))
        
        if self.pinned_msg_id is not None:
            data.write(Int(self.pinned_msg_id))
        
        if self.folder_id is not None:
            data.write(Int(self.folder_id))
        
        if self.call is not None:
            data.write(self.call.write())
        
        if self.ttl_period is not None:
            data.write(Int(self.ttl_period))
        
        if self.groupcall_default_join_as is not None:
            data.write(self.groupcall_default_join_as.write())
        
        if self.theme_emoticon is not None:
            data.write(String(self.theme_emoticon))
        
        return data.getvalue()
