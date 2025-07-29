from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Vector
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class Updates(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Updates`.

    Details:
        - Layer: ``135``
        - ID: ``0x74ae4240``

    Parameters:
        updates: List of :obj:`Update <pyeitaa.raw.base.Update>`
        users: List of :obj:`User <pyeitaa.raw.base.User>`
        chats: List of :obj:`Chat <pyeitaa.raw.base.Chat>`
        date: ``int`` ``32-bit``
        seq: ``int`` ``32-bit``

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

    __slots__: List[str] = ["updates", "users", "chats", "date", "seq"]

    ID = 0x74ae4240
    QUALNAME = "types.Updates"

    def __init__(self, *, updates: List["raw.base.Update"], users: List["raw.base.User"], chats: List["raw.base.Chat"], date: int, seq: int) -> None:
        self.updates = updates  # Vector<Update>
        self.users = users  # Vector<User>
        self.chats = chats  # Vector<Chat>
        self.date = date  # int
        self.seq = seq  # int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        updates = TLObject.read(data)
        
        users = TLObject.read(data)
        
        chats = TLObject.read(data)
        
        date = Int.read(data)
        
        seq = Int.read(data)
        
        return Updates(updates=updates, users=users, chats=chats, date=date, seq=seq)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Vector(self.updates))
        
        data.write(Vector(self.users))
        
        data.write(Vector(self.chats))
        
        data.write(Int(self.date))
        
        data.write(Int(self.seq))
        
        return data.getvalue()
