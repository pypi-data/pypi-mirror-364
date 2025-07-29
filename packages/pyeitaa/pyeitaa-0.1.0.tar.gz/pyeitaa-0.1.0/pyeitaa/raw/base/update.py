from typing import Union
from pyeitaa import raw

Update = Union[raw.types.UpdateBotCallbackQuery, raw.types.UpdateBotCommands, raw.types.UpdateBotInlineQuery, raw.types.UpdateBotInlineSend, raw.types.UpdateBotPrecheckoutQuery, raw.types.UpdateBotShippingQuery, raw.types.UpdateBotStopped, raw.types.UpdateBotWebhookJSON, raw.types.UpdateBotWebhookJSONQuery, raw.types.UpdateChannel, raw.types.UpdateChannelAvailableMessages, raw.types.UpdateChannelMessageForwards, raw.types.UpdateChannelMessageViews, raw.types.UpdateChannelParticipant, raw.types.UpdateChannelReadMessagesContents, raw.types.UpdateChannelTooLong, raw.types.UpdateChannelUserTyping, raw.types.UpdateChannelWebPage, raw.types.UpdateChat, raw.types.UpdateChatDefaultBannedRights, raw.types.UpdateChatParticipant, raw.types.UpdateChatParticipantAdd, raw.types.UpdateChatParticipantAdmin, raw.types.UpdateChatParticipantDelete, raw.types.UpdateChatParticipants, raw.types.UpdateChatUserTyping, raw.types.UpdateConfig, raw.types.UpdateContactsReset, raw.types.UpdateDcOptions, raw.types.UpdateDeleteChannelMessages, raw.types.UpdateDeleteMessages, raw.types.UpdateDeleteScheduledMessages, raw.types.UpdateDialogFilter, raw.types.UpdateDialogFilterOrder, raw.types.UpdateDialogFilters, raw.types.UpdateDialogPinned, raw.types.UpdateDialogUnreadMark, raw.types.UpdateDraftMessage, raw.types.UpdateEditChannelMessage, raw.types.UpdateEditMessage, raw.types.UpdateEncryptedChatTyping, raw.types.UpdateEncryptedMessagesRead, raw.types.UpdateEncryption, raw.types.UpdateFavedStickers, raw.types.UpdateFolderPeers, raw.types.UpdateGeoLiveViewed, raw.types.UpdateGroupCall, raw.types.UpdateGroupCallConnection, raw.types.UpdateGroupCallParticipants, raw.types.UpdateInlineBotCallbackQuery, raw.types.UpdateLangPack, raw.types.UpdateLangPackTooLong, raw.types.UpdateLoginToken, raw.types.UpdateMessageID, raw.types.UpdateMessagePoll, raw.types.UpdateMessagePollVote, raw.types.UpdateNewChannelMessage, raw.types.UpdateNewEncryptedMessage, raw.types.UpdateNewMessage, raw.types.UpdateNewScheduledMessage, raw.types.UpdateNewStickerSet, raw.types.UpdateNotifySettings, raw.types.UpdatePeerBlocked, raw.types.UpdatePeerHistoryTTL, raw.types.UpdatePeerLocated, raw.types.UpdatePeerSettings, raw.types.UpdatePhoneCall, raw.types.UpdatePhoneCallSignalingData, raw.types.UpdatePinnedChannelMessages, raw.types.UpdatePinnedDialogs, raw.types.UpdatePinnedMessages, raw.types.UpdatePrivacy, raw.types.UpdatePtsChanged, raw.types.UpdateReadChannelDiscussionInbox, raw.types.UpdateReadChannelDiscussionOutbox, raw.types.UpdateReadChannelInbox, raw.types.UpdateReadChannelOutbox, raw.types.UpdateReadFeaturedStickers, raw.types.UpdateReadHistoryInbox, raw.types.UpdateReadHistoryOutbox, raw.types.UpdateReadMessagesContents, raw.types.UpdateRecentStickers, raw.types.UpdateSavedGifs, raw.types.UpdateServiceNotification, raw.types.UpdateStickerSets, raw.types.UpdateStickerSetsOrder, raw.types.UpdateTheme, raw.types.UpdateUserName, raw.types.UpdateUserPhone, raw.types.UpdateUserPhoto, raw.types.UpdateUserStatus, raw.types.UpdateUserTyping, raw.types.UpdateWebPage]


# noinspection PyRedeclaration
class Update:
    """This base type has 93 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`UpdateBotCallbackQuery <pyeitaa.raw.types.UpdateBotCallbackQuery>`
            - :obj:`UpdateBotCommands <pyeitaa.raw.types.UpdateBotCommands>`
            - :obj:`UpdateBotInlineQuery <pyeitaa.raw.types.UpdateBotInlineQuery>`
            - :obj:`UpdateBotInlineSend <pyeitaa.raw.types.UpdateBotInlineSend>`
            - :obj:`UpdateBotPrecheckoutQuery <pyeitaa.raw.types.UpdateBotPrecheckoutQuery>`
            - :obj:`UpdateBotShippingQuery <pyeitaa.raw.types.UpdateBotShippingQuery>`
            - :obj:`UpdateBotStopped <pyeitaa.raw.types.UpdateBotStopped>`
            - :obj:`UpdateBotWebhookJSON <pyeitaa.raw.types.UpdateBotWebhookJSON>`
            - :obj:`UpdateBotWebhookJSONQuery <pyeitaa.raw.types.UpdateBotWebhookJSONQuery>`
            - :obj:`UpdateChannel <pyeitaa.raw.types.UpdateChannel>`
            - :obj:`UpdateChannelAvailableMessages <pyeitaa.raw.types.UpdateChannelAvailableMessages>`
            - :obj:`UpdateChannelMessageForwards <pyeitaa.raw.types.UpdateChannelMessageForwards>`
            - :obj:`UpdateChannelMessageViews <pyeitaa.raw.types.UpdateChannelMessageViews>`
            - :obj:`UpdateChannelParticipant <pyeitaa.raw.types.UpdateChannelParticipant>`
            - :obj:`UpdateChannelReadMessagesContents <pyeitaa.raw.types.UpdateChannelReadMessagesContents>`
            - :obj:`UpdateChannelTooLong <pyeitaa.raw.types.UpdateChannelTooLong>`
            - :obj:`UpdateChannelUserTyping <pyeitaa.raw.types.UpdateChannelUserTyping>`
            - :obj:`UpdateChannelWebPage <pyeitaa.raw.types.UpdateChannelWebPage>`
            - :obj:`UpdateChat <pyeitaa.raw.types.UpdateChat>`
            - :obj:`UpdateChatDefaultBannedRights <pyeitaa.raw.types.UpdateChatDefaultBannedRights>`
            - :obj:`UpdateChatParticipant <pyeitaa.raw.types.UpdateChatParticipant>`
            - :obj:`UpdateChatParticipantAdd <pyeitaa.raw.types.UpdateChatParticipantAdd>`
            - :obj:`UpdateChatParticipantAdmin <pyeitaa.raw.types.UpdateChatParticipantAdmin>`
            - :obj:`UpdateChatParticipantDelete <pyeitaa.raw.types.UpdateChatParticipantDelete>`
            - :obj:`UpdateChatParticipants <pyeitaa.raw.types.UpdateChatParticipants>`
            - :obj:`UpdateChatUserTyping <pyeitaa.raw.types.UpdateChatUserTyping>`
            - :obj:`UpdateConfig <pyeitaa.raw.types.UpdateConfig>`
            - :obj:`UpdateContactsReset <pyeitaa.raw.types.UpdateContactsReset>`
            - :obj:`UpdateDcOptions <pyeitaa.raw.types.UpdateDcOptions>`
            - :obj:`UpdateDeleteChannelMessages <pyeitaa.raw.types.UpdateDeleteChannelMessages>`
            - :obj:`UpdateDeleteMessages <pyeitaa.raw.types.UpdateDeleteMessages>`
            - :obj:`UpdateDeleteScheduledMessages <pyeitaa.raw.types.UpdateDeleteScheduledMessages>`
            - :obj:`UpdateDialogFilter <pyeitaa.raw.types.UpdateDialogFilter>`
            - :obj:`UpdateDialogFilterOrder <pyeitaa.raw.types.UpdateDialogFilterOrder>`
            - :obj:`UpdateDialogFilters <pyeitaa.raw.types.UpdateDialogFilters>`
            - :obj:`UpdateDialogPinned <pyeitaa.raw.types.UpdateDialogPinned>`
            - :obj:`UpdateDialogUnreadMark <pyeitaa.raw.types.UpdateDialogUnreadMark>`
            - :obj:`UpdateDraftMessage <pyeitaa.raw.types.UpdateDraftMessage>`
            - :obj:`UpdateEditChannelMessage <pyeitaa.raw.types.UpdateEditChannelMessage>`
            - :obj:`UpdateEditMessage <pyeitaa.raw.types.UpdateEditMessage>`
            - :obj:`UpdateEncryptedChatTyping <pyeitaa.raw.types.UpdateEncryptedChatTyping>`
            - :obj:`UpdateEncryptedMessagesRead <pyeitaa.raw.types.UpdateEncryptedMessagesRead>`
            - :obj:`UpdateEncryption <pyeitaa.raw.types.UpdateEncryption>`
            - :obj:`UpdateFavedStickers <pyeitaa.raw.types.UpdateFavedStickers>`
            - :obj:`UpdateFolderPeers <pyeitaa.raw.types.UpdateFolderPeers>`
            - :obj:`UpdateGeoLiveViewed <pyeitaa.raw.types.UpdateGeoLiveViewed>`
            - :obj:`UpdateGroupCall <pyeitaa.raw.types.UpdateGroupCall>`
            - :obj:`UpdateGroupCallConnection <pyeitaa.raw.types.UpdateGroupCallConnection>`
            - :obj:`UpdateGroupCallParticipants <pyeitaa.raw.types.UpdateGroupCallParticipants>`
            - :obj:`UpdateInlineBotCallbackQuery <pyeitaa.raw.types.UpdateInlineBotCallbackQuery>`
            - :obj:`UpdateLangPack <pyeitaa.raw.types.UpdateLangPack>`
            - :obj:`UpdateLangPackTooLong <pyeitaa.raw.types.UpdateLangPackTooLong>`
            - :obj:`UpdateLoginToken <pyeitaa.raw.types.UpdateLoginToken>`
            - :obj:`UpdateMessageID <pyeitaa.raw.types.UpdateMessageID>`
            - :obj:`UpdateMessagePoll <pyeitaa.raw.types.UpdateMessagePoll>`
            - :obj:`UpdateMessagePollVote <pyeitaa.raw.types.UpdateMessagePollVote>`
            - :obj:`UpdateNewChannelMessage <pyeitaa.raw.types.UpdateNewChannelMessage>`
            - :obj:`UpdateNewEncryptedMessage <pyeitaa.raw.types.UpdateNewEncryptedMessage>`
            - :obj:`UpdateNewMessage <pyeitaa.raw.types.UpdateNewMessage>`
            - :obj:`UpdateNewScheduledMessage <pyeitaa.raw.types.UpdateNewScheduledMessage>`
            - :obj:`UpdateNewStickerSet <pyeitaa.raw.types.UpdateNewStickerSet>`
            - :obj:`UpdateNotifySettings <pyeitaa.raw.types.UpdateNotifySettings>`
            - :obj:`UpdatePeerBlocked <pyeitaa.raw.types.UpdatePeerBlocked>`
            - :obj:`UpdatePeerHistoryTTL <pyeitaa.raw.types.UpdatePeerHistoryTTL>`
            - :obj:`UpdatePeerLocated <pyeitaa.raw.types.UpdatePeerLocated>`
            - :obj:`UpdatePeerSettings <pyeitaa.raw.types.UpdatePeerSettings>`
            - :obj:`UpdatePhoneCall <pyeitaa.raw.types.UpdatePhoneCall>`
            - :obj:`UpdatePhoneCallSignalingData <pyeitaa.raw.types.UpdatePhoneCallSignalingData>`
            - :obj:`UpdatePinnedChannelMessages <pyeitaa.raw.types.UpdatePinnedChannelMessages>`
            - :obj:`UpdatePinnedDialogs <pyeitaa.raw.types.UpdatePinnedDialogs>`
            - :obj:`UpdatePinnedMessages <pyeitaa.raw.types.UpdatePinnedMessages>`
            - :obj:`UpdatePrivacy <pyeitaa.raw.types.UpdatePrivacy>`
            - :obj:`UpdatePtsChanged <pyeitaa.raw.types.UpdatePtsChanged>`
            - :obj:`UpdateReadChannelDiscussionInbox <pyeitaa.raw.types.UpdateReadChannelDiscussionInbox>`
            - :obj:`UpdateReadChannelDiscussionOutbox <pyeitaa.raw.types.UpdateReadChannelDiscussionOutbox>`
            - :obj:`UpdateReadChannelInbox <pyeitaa.raw.types.UpdateReadChannelInbox>`
            - :obj:`UpdateReadChannelOutbox <pyeitaa.raw.types.UpdateReadChannelOutbox>`
            - :obj:`UpdateReadFeaturedStickers <pyeitaa.raw.types.UpdateReadFeaturedStickers>`
            - :obj:`UpdateReadHistoryInbox <pyeitaa.raw.types.UpdateReadHistoryInbox>`
            - :obj:`UpdateReadHistoryOutbox <pyeitaa.raw.types.UpdateReadHistoryOutbox>`
            - :obj:`UpdateReadMessagesContents <pyeitaa.raw.types.UpdateReadMessagesContents>`
            - :obj:`UpdateRecentStickers <pyeitaa.raw.types.UpdateRecentStickers>`
            - :obj:`UpdateSavedGifs <pyeitaa.raw.types.UpdateSavedGifs>`
            - :obj:`UpdateServiceNotification <pyeitaa.raw.types.UpdateServiceNotification>`
            - :obj:`UpdateStickerSets <pyeitaa.raw.types.UpdateStickerSets>`
            - :obj:`UpdateStickerSetsOrder <pyeitaa.raw.types.UpdateStickerSetsOrder>`
            - :obj:`UpdateTheme <pyeitaa.raw.types.UpdateTheme>`
            - :obj:`UpdateUserName <pyeitaa.raw.types.UpdateUserName>`
            - :obj:`UpdateUserPhone <pyeitaa.raw.types.UpdateUserPhone>`
            - :obj:`UpdateUserPhoto <pyeitaa.raw.types.UpdateUserPhoto>`
            - :obj:`UpdateUserStatus <pyeitaa.raw.types.UpdateUserStatus>`
            - :obj:`UpdateUserTyping <pyeitaa.raw.types.UpdateUserTyping>`
            - :obj:`UpdateWebPage <pyeitaa.raw.types.UpdateWebPage>`
    """

    QUALNAME = "pyeitaa.raw.base.Update"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
