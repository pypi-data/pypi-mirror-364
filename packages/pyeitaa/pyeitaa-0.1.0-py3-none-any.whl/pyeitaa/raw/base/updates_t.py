from typing import Union
from pyeitaa import raw

Updates = Union[raw.types.UpdateShort, raw.types.UpdateShortChatMessage, raw.types.UpdateShortMessage, raw.types.UpdateShortSentMessage, raw.types.Updates, raw.types.UpdatesCombined, raw.types.UpdatesTooLong]


# noinspection PyRedeclaration
class Updates:
    """This base type has 7 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`UpdateShort <pyeitaa.raw.types.UpdateShort>`
            - :obj:`UpdateShortChatMessage <pyeitaa.raw.types.UpdateShortChatMessage>`
            - :obj:`UpdateShortMessage <pyeitaa.raw.types.UpdateShortMessage>`
            - :obj:`UpdateShortSentMessage <pyeitaa.raw.types.UpdateShortSentMessage>`
            - :obj:`Updates <pyeitaa.raw.types.Updates>`
            - :obj:`UpdatesCombined <pyeitaa.raw.types.UpdatesCombined>`
            - :obj:`UpdatesTooLong <pyeitaa.raw.types.UpdatesTooLong>`

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

    QUALNAME = "pyeitaa.raw.base.Updates"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
