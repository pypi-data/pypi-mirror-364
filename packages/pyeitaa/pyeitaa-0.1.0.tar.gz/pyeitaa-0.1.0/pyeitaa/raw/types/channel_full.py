from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class ChannelFull(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.ChatFull`.

    Details:
        - Layer: ``135``
        - ID: ``-0x164d85e9``

    Parameters:
        id: ``int`` ``64-bit``
        about: ``str``
        read_inbox_max_id: ``int`` ``32-bit``
        read_outbox_max_id: ``int`` ``32-bit``
        unread_count: ``int`` ``32-bit``
        chat_photo: :obj:`Photo <pyeitaa.raw.base.Photo>`
        notify_settings: :obj:`PeerNotifySettings <pyeitaa.raw.base.PeerNotifySettings>`
        bot_info: List of :obj:`BotInfo <pyeitaa.raw.base.BotInfo>`
        pts: ``int`` ``32-bit``
        can_view_participants (optional): ``bool``
        can_set_username (optional): ``bool``
        can_set_stickers (optional): ``bool``
        hidden_prehistory (optional): ``bool``
        can_set_location (optional): ``bool``
        has_scheduled (optional): ``bool``
        can_view_stats (optional): ``bool``
        blocked (optional): ``bool``
        participants_count (optional): ``int`` ``32-bit``
        admins_count (optional): ``int`` ``32-bit``
        kicked_count (optional): ``int`` ``32-bit``
        banned_count (optional): ``int`` ``32-bit``
        online_count (optional): ``int`` ``32-bit``
        exported_invite (optional): :obj:`ExportedChatInvite <pyeitaa.raw.base.ExportedChatInvite>`
        migrated_from_chat_id (optional): ``int`` ``64-bit``
        migrated_from_max_id (optional): ``int`` ``32-bit``
        pinned_msg_id (optional): ``int`` ``32-bit``
        stickerset (optional): :obj:`StickerSet <pyeitaa.raw.base.StickerSet>`
        available_min_id (optional): ``int`` ``32-bit``
        folder_id (optional): ``int`` ``32-bit``
        linked_chat_id (optional): ``int`` ``64-bit``
        location (optional): :obj:`ChannelLocation <pyeitaa.raw.base.ChannelLocation>`
        slowmode_seconds (optional): ``int`` ``32-bit``
        slowmode_next_send_date (optional): ``int`` ``32-bit``
        stats_dc (optional): ``int`` ``32-bit``
        call (optional): :obj:`InputGroupCall <pyeitaa.raw.base.InputGroupCall>`
        ttl_period (optional): ``int`` ``32-bit``
        pending_suggestions (optional): List of ``str``
        groupcall_default_join_as (optional): :obj:`Peer <pyeitaa.raw.base.Peer>`
        theme_emoticon (optional): ``str``
        business_location (optional): ``int`` ``32-bit``
        default_send_as (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["id", "about", "read_inbox_max_id", "read_outbox_max_id", "unread_count", "chat_photo", "notify_settings", "bot_info", "pts", "can_view_participants", "can_set_username", "can_set_stickers", "hidden_prehistory", "can_set_location", "has_scheduled", "can_view_stats", "blocked", "participants_count", "admins_count", "kicked_count", "banned_count", "online_count", "exported_invite", "migrated_from_chat_id", "migrated_from_max_id", "pinned_msg_id", "stickerset", "available_min_id", "folder_id", "linked_chat_id", "location", "slowmode_seconds", "slowmode_next_send_date", "stats_dc", "call", "ttl_period", "pending_suggestions", "groupcall_default_join_as", "theme_emoticon", "business_location", "default_send_as"]

    ID = -0x164d85e9
    QUALNAME = "types.ChannelFull"

    def __init__(self, *, id: int, about: str, read_inbox_max_id: int, read_outbox_max_id: int, unread_count: int, chat_photo: "raw.base.Photo", notify_settings: "raw.base.PeerNotifySettings", bot_info: List["raw.base.BotInfo"], pts: int, can_view_participants: Optional[bool] = None, can_set_username: Optional[bool] = None, can_set_stickers: Optional[bool] = None, hidden_prehistory: Optional[bool] = None, can_set_location: Optional[bool] = None, has_scheduled: Optional[bool] = None, can_view_stats: Optional[bool] = None, blocked: Optional[bool] = None, participants_count: Optional[int] = None, admins_count: Optional[int] = None, kicked_count: Optional[int] = None, banned_count: Optional[int] = None, online_count: Optional[int] = None, exported_invite: "raw.base.ExportedChatInvite" = None, migrated_from_chat_id: Optional[int] = None, migrated_from_max_id: Optional[int] = None, pinned_msg_id: Optional[int] = None, stickerset: "raw.base.StickerSet" = None, available_min_id: Optional[int] = None, folder_id: Optional[int] = None, linked_chat_id: Optional[int] = None, location: "raw.base.ChannelLocation" = None, slowmode_seconds: Optional[int] = None, slowmode_next_send_date: Optional[int] = None, stats_dc: Optional[int] = None, call: "raw.base.InputGroupCall" = None, ttl_period: Optional[int] = None, pending_suggestions: Optional[List[str]] = None, groupcall_default_join_as: "raw.base.Peer" = None, theme_emoticon: Optional[str] = None, business_location: Optional[int] = None, default_send_as: Optional[int] = None) -> None:
        self.id = id  # long
        self.about = about  # string
        self.read_inbox_max_id = read_inbox_max_id  # int
        self.read_outbox_max_id = read_outbox_max_id  # int
        self.unread_count = unread_count  # int
        self.chat_photo = chat_photo  # Photo
        self.notify_settings = notify_settings  # PeerNotifySettings
        self.bot_info = bot_info  # Vector<BotInfo>
        self.pts = pts  # int
        self.can_view_participants = can_view_participants  # flags.3?true
        self.can_set_username = can_set_username  # flags.6?true
        self.can_set_stickers = can_set_stickers  # flags.7?true
        self.hidden_prehistory = hidden_prehistory  # flags.10?true
        self.can_set_location = can_set_location  # flags.16?true
        self.has_scheduled = has_scheduled  # flags.19?true
        self.can_view_stats = can_view_stats  # flags.20?true
        self.blocked = blocked  # flags.22?true
        self.participants_count = participants_count  # flags.0?int
        self.admins_count = admins_count  # flags.1?int
        self.kicked_count = kicked_count  # flags.2?int
        self.banned_count = banned_count  # flags.2?int
        self.online_count = online_count  # flags.13?int
        self.exported_invite = exported_invite  # flags.23?ExportedChatInvite
        self.migrated_from_chat_id = migrated_from_chat_id  # flags.4?long
        self.migrated_from_max_id = migrated_from_max_id  # flags.4?int
        self.pinned_msg_id = pinned_msg_id  # flags.5?int
        self.stickerset = stickerset  # flags.8?StickerSet
        self.available_min_id = available_min_id  # flags.9?int
        self.folder_id = folder_id  # flags.11?int
        self.linked_chat_id = linked_chat_id  # flags.14?long
        self.location = location  # flags.15?ChannelLocation
        self.slowmode_seconds = slowmode_seconds  # flags.17?int
        self.slowmode_next_send_date = slowmode_next_send_date  # flags.18?int
        self.stats_dc = stats_dc  # flags.12?int
        self.call = call  # flags.21?InputGroupCall
        self.ttl_period = ttl_period  # flags.24?int
        self.pending_suggestions = pending_suggestions  # flags.25?Vector<string>
        self.groupcall_default_join_as = groupcall_default_join_as  # flags.26?Peer
        self.theme_emoticon = theme_emoticon  # flags.27?string
        self.business_location = business_location  # flags.28?int
        self.default_send_as = default_send_as  # flags.29?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        can_view_participants = True if flags & (1 << 3) else False
        can_set_username = True if flags & (1 << 6) else False
        can_set_stickers = True if flags & (1 << 7) else False
        hidden_prehistory = True if flags & (1 << 10) else False
        can_set_location = True if flags & (1 << 16) else False
        has_scheduled = True if flags & (1 << 19) else False
        can_view_stats = True if flags & (1 << 20) else False
        blocked = True if flags & (1 << 22) else False
        id = Long.read(data)
        
        about = String.read(data)
        
        participants_count = Int.read(data) if flags & (1 << 0) else None
        admins_count = Int.read(data) if flags & (1 << 1) else None
        kicked_count = Int.read(data) if flags & (1 << 2) else None
        banned_count = Int.read(data) if flags & (1 << 2) else None
        online_count = Int.read(data) if flags & (1 << 13) else None
        read_inbox_max_id = Int.read(data)
        
        read_outbox_max_id = Int.read(data)
        
        unread_count = Int.read(data)
        
        chat_photo = TLObject.read(data)
        
        notify_settings = TLObject.read(data)
        
        exported_invite = TLObject.read(data) if flags & (1 << 23) else None
        
        bot_info = TLObject.read(data)
        
        migrated_from_chat_id = Long.read(data) if flags & (1 << 4) else None
        migrated_from_max_id = Int.read(data) if flags & (1 << 4) else None
        pinned_msg_id = Int.read(data) if flags & (1 << 5) else None
        stickerset = TLObject.read(data) if flags & (1 << 8) else None
        
        available_min_id = Int.read(data) if flags & (1 << 9) else None
        folder_id = Int.read(data) if flags & (1 << 11) else None
        linked_chat_id = Long.read(data) if flags & (1 << 14) else None
        location = TLObject.read(data) if flags & (1 << 15) else None
        
        slowmode_seconds = Int.read(data) if flags & (1 << 17) else None
        slowmode_next_send_date = Int.read(data) if flags & (1 << 18) else None
        stats_dc = Int.read(data) if flags & (1 << 12) else None
        pts = Int.read(data)
        
        call = TLObject.read(data) if flags & (1 << 21) else None
        
        ttl_period = Int.read(data) if flags & (1 << 24) else None
        pending_suggestions = TLObject.read(data, String) if flags & (1 << 25) else []
        
        groupcall_default_join_as = TLObject.read(data) if flags & (1 << 26) else None
        
        theme_emoticon = String.read(data) if flags & (1 << 27) else None
        business_location = Int.read(data) if flags & (1 << 28) else None
        default_send_as = Int.read(data) if flags & (1 << 29) else None
        return ChannelFull(id=id, about=about, read_inbox_max_id=read_inbox_max_id, read_outbox_max_id=read_outbox_max_id, unread_count=unread_count, chat_photo=chat_photo, notify_settings=notify_settings, bot_info=bot_info, pts=pts, can_view_participants=can_view_participants, can_set_username=can_set_username, can_set_stickers=can_set_stickers, hidden_prehistory=hidden_prehistory, can_set_location=can_set_location, has_scheduled=has_scheduled, can_view_stats=can_view_stats, blocked=blocked, participants_count=participants_count, admins_count=admins_count, kicked_count=kicked_count, banned_count=banned_count, online_count=online_count, exported_invite=exported_invite, migrated_from_chat_id=migrated_from_chat_id, migrated_from_max_id=migrated_from_max_id, pinned_msg_id=pinned_msg_id, stickerset=stickerset, available_min_id=available_min_id, folder_id=folder_id, linked_chat_id=linked_chat_id, location=location, slowmode_seconds=slowmode_seconds, slowmode_next_send_date=slowmode_next_send_date, stats_dc=stats_dc, call=call, ttl_period=ttl_period, pending_suggestions=pending_suggestions, groupcall_default_join_as=groupcall_default_join_as, theme_emoticon=theme_emoticon, business_location=business_location, default_send_as=default_send_as)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 3) if self.can_view_participants else 0
        flags |= (1 << 6) if self.can_set_username else 0
        flags |= (1 << 7) if self.can_set_stickers else 0
        flags |= (1 << 10) if self.hidden_prehistory else 0
        flags |= (1 << 16) if self.can_set_location else 0
        flags |= (1 << 19) if self.has_scheduled else 0
        flags |= (1 << 20) if self.can_view_stats else 0
        flags |= (1 << 22) if self.blocked else 0
        flags |= (1 << 0) if self.participants_count is not None else 0
        flags |= (1 << 1) if self.admins_count is not None else 0
        flags |= (1 << 2) if self.kicked_count is not None else 0
        flags |= (1 << 2) if self.banned_count is not None else 0
        flags |= (1 << 13) if self.online_count is not None else 0
        flags |= (1 << 23) if self.exported_invite is not None else 0
        flags |= (1 << 4) if self.migrated_from_chat_id is not None else 0
        flags |= (1 << 4) if self.migrated_from_max_id is not None else 0
        flags |= (1 << 5) if self.pinned_msg_id is not None else 0
        flags |= (1 << 8) if self.stickerset is not None else 0
        flags |= (1 << 9) if self.available_min_id is not None else 0
        flags |= (1 << 11) if self.folder_id is not None else 0
        flags |= (1 << 14) if self.linked_chat_id is not None else 0
        flags |= (1 << 15) if self.location is not None else 0
        flags |= (1 << 17) if self.slowmode_seconds is not None else 0
        flags |= (1 << 18) if self.slowmode_next_send_date is not None else 0
        flags |= (1 << 12) if self.stats_dc is not None else 0
        flags |= (1 << 21) if self.call is not None else 0
        flags |= (1 << 24) if self.ttl_period is not None else 0
        flags |= (1 << 25) if self.pending_suggestions is not None else 0
        flags |= (1 << 26) if self.groupcall_default_join_as is not None else 0
        flags |= (1 << 27) if self.theme_emoticon is not None else 0
        flags |= (1 << 28) if self.business_location is not None else 0
        flags |= (1 << 29) if self.default_send_as is not None else 0
        data.write(Int(flags))
        
        data.write(Long(self.id))
        
        data.write(String(self.about))
        
        if self.participants_count is not None:
            data.write(Int(self.participants_count))
        
        if self.admins_count is not None:
            data.write(Int(self.admins_count))
        
        if self.kicked_count is not None:
            data.write(Int(self.kicked_count))
        
        if self.banned_count is not None:
            data.write(Int(self.banned_count))
        
        if self.online_count is not None:
            data.write(Int(self.online_count))
        
        data.write(Int(self.read_inbox_max_id))
        
        data.write(Int(self.read_outbox_max_id))
        
        data.write(Int(self.unread_count))
        
        data.write(self.chat_photo.write())
        
        data.write(self.notify_settings.write())
        
        if self.exported_invite is not None:
            data.write(self.exported_invite.write())
        
        data.write(Vector(self.bot_info))
        
        if self.migrated_from_chat_id is not None:
            data.write(Long(self.migrated_from_chat_id))
        
        if self.migrated_from_max_id is not None:
            data.write(Int(self.migrated_from_max_id))
        
        if self.pinned_msg_id is not None:
            data.write(Int(self.pinned_msg_id))
        
        if self.stickerset is not None:
            data.write(self.stickerset.write())
        
        if self.available_min_id is not None:
            data.write(Int(self.available_min_id))
        
        if self.folder_id is not None:
            data.write(Int(self.folder_id))
        
        if self.linked_chat_id is not None:
            data.write(Long(self.linked_chat_id))
        
        if self.location is not None:
            data.write(self.location.write())
        
        if self.slowmode_seconds is not None:
            data.write(Int(self.slowmode_seconds))
        
        if self.slowmode_next_send_date is not None:
            data.write(Int(self.slowmode_next_send_date))
        
        if self.stats_dc is not None:
            data.write(Int(self.stats_dc))
        
        data.write(Int(self.pts))
        
        if self.call is not None:
            data.write(self.call.write())
        
        if self.ttl_period is not None:
            data.write(Int(self.ttl_period))
        
        if self.pending_suggestions is not None:
            data.write(Vector(self.pending_suggestions, String))
        
        if self.groupcall_default_join_as is not None:
            data.write(self.groupcall_default_join_as.write())
        
        if self.theme_emoticon is not None:
            data.write(String(self.theme_emoticon))
        
        if self.business_location is not None:
            data.write(Int(self.business_location))
        
        if self.default_send_as is not None:
            data.write(Int(self.default_send_as))
        
        return data.getvalue()
