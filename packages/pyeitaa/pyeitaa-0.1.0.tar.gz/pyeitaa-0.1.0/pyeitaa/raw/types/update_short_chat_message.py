from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Optional, Any, Self


class UpdateShortChatMessage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Updates`.

    Details:
        - Layer: ``135``
        - ID: ``0x4d6deea5``

    Parameters:
        id: ``int`` ``32-bit``
        from_id: ``int`` ``64-bit``
        chat_id: ``int`` ``64-bit``
        message: ``str``
        pts: ``int`` ``32-bit``
        pts_count: ``int`` ``32-bit``
        date: ``int`` ``32-bit``
        out (optional): ``bool``
        mentioned (optional): ``bool``
        media_unread (optional): ``bool``
        silent (optional): ``bool``
        fwd_from (optional): :obj:`MessageFwdHeader <pyeitaa.raw.base.MessageFwdHeader>`
        via_bot_id (optional): ``int`` ``64-bit``
        reply_to (optional): :obj:`MessageReplyHeader <pyeitaa.raw.base.MessageReplyHeader>`
        entities (optional): List of :obj:`MessageEntity <pyeitaa.raw.base.MessageEntity>`
        ttl_period (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 65 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.GetNotifyExceptions <pyeitaa.raw.functions.account.GetNotifyExceptions>`
            - :obj:`contacts.DeleteContacts <pyeitaa.raw.functions.contacts.DeleteContacts>`
            - :obj:`contacts.AddContact <pyeitaa.raw.functions.contacts.AddContact>`
            - :obj:`contacts.AcceptContact <pyeitaa.raw.functions.contacts.AcceptContact>`
            - :obj:`contacts.GetLocated <pyeitaa.raw.functions.contacts.GetLocated>`
            - :obj:`contacts.BlockFromReplies <pyeitaa.raw.functions.contacts.BlockFromReplies>`
            - :obj:`messages.SendMessage <pyeitaa.raw.functions.messages.SendMessage>`
            - :obj:`messages.SendMedia <pyeitaa.raw.functions.messages.SendMedia>`
            - :obj:`messages.ForwardMessages <pyeitaa.raw.functions.messages.ForwardMessages>`
            - :obj:`messages.EditChatTitle <pyeitaa.raw.functions.messages.EditChatTitle>`
            - :obj:`messages.EditChatPhoto <pyeitaa.raw.functions.messages.EditChatPhoto>`
            - :obj:`messages.AddChatUser <pyeitaa.raw.functions.messages.AddChatUser>`
            - :obj:`messages.DeleteChatUser <pyeitaa.raw.functions.messages.DeleteChatUser>`
            - :obj:`messages.CreateChat <pyeitaa.raw.functions.messages.CreateChat>`
            - :obj:`messages.ImportChatInvite <pyeitaa.raw.functions.messages.ImportChatInvite>`
            - :obj:`messages.StartBot <pyeitaa.raw.functions.messages.StartBot>`
            - :obj:`messages.MigrateChat <pyeitaa.raw.functions.messages.MigrateChat>`
            - :obj:`messages.SendInlineBotResult <pyeitaa.raw.functions.messages.SendInlineBotResult>`
            - :obj:`messages.EditMessage <pyeitaa.raw.functions.messages.EditMessage>`
            - :obj:`messages.GetAllDrafts <pyeitaa.raw.functions.messages.GetAllDrafts>`
            - :obj:`messages.SetGameScore <pyeitaa.raw.functions.messages.SetGameScore>`
            - :obj:`messages.SendScreenshotNotification <pyeitaa.raw.functions.messages.SendScreenshotNotification>`
            - :obj:`messages.SendMultiMedia <pyeitaa.raw.functions.messages.SendMultiMedia>`
            - :obj:`messages.UpdatePinnedMessage <pyeitaa.raw.functions.messages.UpdatePinnedMessage>`
            - :obj:`messages.SendVote <pyeitaa.raw.functions.messages.SendVote>`
            - :obj:`messages.GetPollResults <pyeitaa.raw.functions.messages.GetPollResults>`
            - :obj:`messages.EditChatDefaultBannedRights <pyeitaa.raw.functions.messages.EditChatDefaultBannedRights>`
            - :obj:`messages.SendScheduledMessages <pyeitaa.raw.functions.messages.SendScheduledMessages>`
            - :obj:`messages.DeleteScheduledMessages <pyeitaa.raw.functions.messages.DeleteScheduledMessages>`
            - :obj:`messages.SetHistoryTTL <pyeitaa.raw.functions.messages.SetHistoryTTL>`
            - :obj:`messages.SetChatTheme <pyeitaa.raw.functions.messages.SetChatTheme>`
            - :obj:`help.GetAppChangelog <pyeitaa.raw.functions.help.GetAppChangelog>`
            - :obj:`channels.CreateChannel <pyeitaa.raw.functions.channels.CreateChannel>`
            - :obj:`channels.EditAdmin <pyeitaa.raw.functions.channels.EditAdmin>`
            - :obj:`channels.EditTitle <pyeitaa.raw.functions.channels.EditTitle>`
            - :obj:`channels.EditPhoto <pyeitaa.raw.functions.channels.EditPhoto>`
            - :obj:`channels.JoinChannel <pyeitaa.raw.functions.channels.JoinChannel>`
            - :obj:`channels.LeaveChannel <pyeitaa.raw.functions.channels.LeaveChannel>`
            - :obj:`channels.InviteToChannel <pyeitaa.raw.functions.channels.InviteToChannel>`
            - :obj:`channels.InviteToChannelLayer84 <pyeitaa.raw.functions.channels.InviteToChannelLayer84>`
            - :obj:`channels.DeleteChannel <pyeitaa.raw.functions.channels.DeleteChannel>`
            - :obj:`channels.ToggleSignatures <pyeitaa.raw.functions.channels.ToggleSignatures>`
            - :obj:`channels.EditBanned <pyeitaa.raw.functions.channels.EditBanned>`
            - :obj:`channels.TogglePreHistoryHidden <pyeitaa.raw.functions.channels.TogglePreHistoryHidden>`
            - :obj:`channels.EditCreator <pyeitaa.raw.functions.channels.EditCreator>`
            - :obj:`channels.ToggleSlowMode <pyeitaa.raw.functions.channels.ToggleSlowMode>`
            - :obj:`channels.ConvertToGigagroup <pyeitaa.raw.functions.channels.ConvertToGigagroup>`
            - :obj:`phone.DiscardCall <pyeitaa.raw.functions.phone.DiscardCall>`
            - :obj:`phone.SetCallRating <pyeitaa.raw.functions.phone.SetCallRating>`
            - :obj:`phone.CreateGroupCall <pyeitaa.raw.functions.phone.CreateGroupCall>`
            - :obj:`phone.JoinGroupCall <pyeitaa.raw.functions.phone.JoinGroupCall>`
            - :obj:`phone.LeaveGroupCall <pyeitaa.raw.functions.phone.LeaveGroupCall>`
            - :obj:`phone.InviteToGroupCall <pyeitaa.raw.functions.phone.InviteToGroupCall>`
            - :obj:`phone.DiscardGroupCall <pyeitaa.raw.functions.phone.DiscardGroupCall>`
            - :obj:`phone.ToggleGroupCallSettings <pyeitaa.raw.functions.phone.ToggleGroupCallSettings>`
            - :obj:`phone.ToggleGroupCallRecord <pyeitaa.raw.functions.phone.ToggleGroupCallRecord>`
            - :obj:`phone.EditGroupCallParticipant <pyeitaa.raw.functions.phone.EditGroupCallParticipant>`
            - :obj:`phone.EditGroupCallTitle <pyeitaa.raw.functions.phone.EditGroupCallTitle>`
            - :obj:`phone.ToggleGroupCallStartSubscription <pyeitaa.raw.functions.phone.ToggleGroupCallStartSubscription>`
            - :obj:`phone.StartScheduledGroupCall <pyeitaa.raw.functions.phone.StartScheduledGroupCall>`
            - :obj:`phone.JoinGroupCallPresentation <pyeitaa.raw.functions.phone.JoinGroupCallPresentation>`
            - :obj:`phone.LeaveGroupCallPresentation <pyeitaa.raw.functions.phone.LeaveGroupCallPresentation>`
            - :obj:`folders.EditPeerFolders <pyeitaa.raw.functions.folders.EditPeerFolders>`
            - :obj:`folders.DeleteFolder <pyeitaa.raw.functions.folders.DeleteFolder>`
            - :obj:`messages.ToggleNoForwards <pyeitaa.raw.functions.messages.ToggleNoForwards>`
    """

    __slots__: List[str] = ["id", "from_id", "chat_id", "message", "pts", "pts_count", "date", "out", "mentioned", "media_unread", "silent", "fwd_from", "via_bot_id", "reply_to", "entities", "ttl_period"]

    ID = 0x4d6deea5
    QUALNAME = "types.UpdateShortChatMessage"

    def __init__(self, *, id: int, from_id: int, chat_id: int, message: str, pts: int, pts_count: int, date: int, out: Optional[bool] = None, mentioned: Optional[bool] = None, media_unread: Optional[bool] = None, silent: Optional[bool] = None, fwd_from: "raw.base.MessageFwdHeader" = None, via_bot_id: Optional[int] = None, reply_to: "raw.base.MessageReplyHeader" = None, entities: Optional[List["raw.base.MessageEntity"]] = None, ttl_period: Optional[int] = None) -> None:
        self.id = id  # int
        self.from_id = from_id  # long
        self.chat_id = chat_id  # long
        self.message = message  # string
        self.pts = pts  # int
        self.pts_count = pts_count  # int
        self.date = date  # int
        self.out = out  # flags.1?true
        self.mentioned = mentioned  # flags.4?true
        self.media_unread = media_unread  # flags.5?true
        self.silent = silent  # flags.13?true
        self.fwd_from = fwd_from  # flags.2?MessageFwdHeader
        self.via_bot_id = via_bot_id  # flags.11?long
        self.reply_to = reply_to  # flags.3?MessageReplyHeader
        self.entities = entities  # flags.7?Vector<MessageEntity>
        self.ttl_period = ttl_period  # flags.25?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        out = True if flags & (1 << 1) else False
        mentioned = True if flags & (1 << 4) else False
        media_unread = True if flags & (1 << 5) else False
        silent = True if flags & (1 << 13) else False
        id = Int.read(data)
        
        from_id = Long.read(data)
        
        chat_id = Long.read(data)
        
        message = String.read(data)
        
        pts = Int.read(data)
        
        pts_count = Int.read(data)
        
        date = Int.read(data)
        
        fwd_from = TLObject.read(data) if flags & (1 << 2) else None
        
        via_bot_id = Long.read(data) if flags & (1 << 11) else None
        reply_to = TLObject.read(data) if flags & (1 << 3) else None
        
        entities = TLObject.read(data) if flags & (1 << 7) else []
        
        ttl_period = Int.read(data) if flags & (1 << 25) else None
        return UpdateShortChatMessage(id=id, from_id=from_id, chat_id=chat_id, message=message, pts=pts, pts_count=pts_count, date=date, out=out, mentioned=mentioned, media_unread=media_unread, silent=silent, fwd_from=fwd_from, via_bot_id=via_bot_id, reply_to=reply_to, entities=entities, ttl_period=ttl_period)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.out else 0
        flags |= (1 << 4) if self.mentioned else 0
        flags |= (1 << 5) if self.media_unread else 0
        flags |= (1 << 13) if self.silent else 0
        flags |= (1 << 2) if self.fwd_from is not None else 0
        flags |= (1 << 11) if self.via_bot_id is not None else 0
        flags |= (1 << 3) if self.reply_to is not None else 0
        flags |= (1 << 7) if self.entities is not None else 0
        flags |= (1 << 25) if self.ttl_period is not None else 0
        data.write(Int(flags))
        
        data.write(Int(self.id))
        
        data.write(Long(self.from_id))
        
        data.write(Long(self.chat_id))
        
        data.write(String(self.message))
        
        data.write(Int(self.pts))
        
        data.write(Int(self.pts_count))
        
        data.write(Int(self.date))
        
        if self.fwd_from is not None:
            data.write(self.fwd_from.write())
        
        if self.via_bot_id is not None:
            data.write(Long(self.via_bot_id))
        
        if self.reply_to is not None:
            data.write(self.reply_to.write())
        
        if self.entities is not None:
            data.write(Vector(self.entities))
        
        if self.ttl_period is not None:
            data.write(Int(self.ttl_period))
        
        return data.getvalue()
