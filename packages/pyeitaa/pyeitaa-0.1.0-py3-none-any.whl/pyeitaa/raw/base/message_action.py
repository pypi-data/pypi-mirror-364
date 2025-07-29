from typing import Union
from pyeitaa import raw

MessageAction = Union[raw.types.MessageActionBotAllowed, raw.types.MessageActionChannelCreate, raw.types.MessageActionChannelMigrateFrom, raw.types.MessageActionChatAddUser, raw.types.MessageActionChatCreate, raw.types.MessageActionChatDeletePhoto, raw.types.MessageActionChatDeleteUser, raw.types.MessageActionChatEditPhoto, raw.types.MessageActionChatEditTitle, raw.types.MessageActionChatJoinedByLink, raw.types.MessageActionChatMigrateTo, raw.types.MessageActionContactSignUp, raw.types.MessageActionCustomAction, raw.types.MessageActionEmpty, raw.types.MessageActionGameScore, raw.types.MessageActionGeoProximityReached, raw.types.MessageActionGroupCall, raw.types.MessageActionGroupCallScheduled, raw.types.MessageActionHistoryClear, raw.types.MessageActionInviteToGroupCall, raw.types.MessageActionPaymentSent, raw.types.MessageActionPaymentSentMe, raw.types.MessageActionPhoneCall, raw.types.MessageActionPinMessage, raw.types.MessageActionScreenshotTaken, raw.types.MessageActionSecureValuesSent, raw.types.MessageActionSecureValuesSentMe, raw.types.MessageActionSetChatTheme, raw.types.MessageActionSetMessagesTTL]


# noinspection PyRedeclaration
class MessageAction:
    """This base type has 29 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`MessageActionBotAllowed <pyeitaa.raw.types.MessageActionBotAllowed>`
            - :obj:`MessageActionChannelCreate <pyeitaa.raw.types.MessageActionChannelCreate>`
            - :obj:`MessageActionChannelMigrateFrom <pyeitaa.raw.types.MessageActionChannelMigrateFrom>`
            - :obj:`MessageActionChatAddUser <pyeitaa.raw.types.MessageActionChatAddUser>`
            - :obj:`MessageActionChatCreate <pyeitaa.raw.types.MessageActionChatCreate>`
            - :obj:`MessageActionChatDeletePhoto <pyeitaa.raw.types.MessageActionChatDeletePhoto>`
            - :obj:`MessageActionChatDeleteUser <pyeitaa.raw.types.MessageActionChatDeleteUser>`
            - :obj:`MessageActionChatEditPhoto <pyeitaa.raw.types.MessageActionChatEditPhoto>`
            - :obj:`MessageActionChatEditTitle <pyeitaa.raw.types.MessageActionChatEditTitle>`
            - :obj:`MessageActionChatJoinedByLink <pyeitaa.raw.types.MessageActionChatJoinedByLink>`
            - :obj:`MessageActionChatMigrateTo <pyeitaa.raw.types.MessageActionChatMigrateTo>`
            - :obj:`MessageActionContactSignUp <pyeitaa.raw.types.MessageActionContactSignUp>`
            - :obj:`MessageActionCustomAction <pyeitaa.raw.types.MessageActionCustomAction>`
            - :obj:`MessageActionEmpty <pyeitaa.raw.types.MessageActionEmpty>`
            - :obj:`MessageActionGameScore <pyeitaa.raw.types.MessageActionGameScore>`
            - :obj:`MessageActionGeoProximityReached <pyeitaa.raw.types.MessageActionGeoProximityReached>`
            - :obj:`MessageActionGroupCall <pyeitaa.raw.types.MessageActionGroupCall>`
            - :obj:`MessageActionGroupCallScheduled <pyeitaa.raw.types.MessageActionGroupCallScheduled>`
            - :obj:`MessageActionHistoryClear <pyeitaa.raw.types.MessageActionHistoryClear>`
            - :obj:`MessageActionInviteToGroupCall <pyeitaa.raw.types.MessageActionInviteToGroupCall>`
            - :obj:`MessageActionPaymentSent <pyeitaa.raw.types.MessageActionPaymentSent>`
            - :obj:`MessageActionPaymentSentMe <pyeitaa.raw.types.MessageActionPaymentSentMe>`
            - :obj:`MessageActionPhoneCall <pyeitaa.raw.types.MessageActionPhoneCall>`
            - :obj:`MessageActionPinMessage <pyeitaa.raw.types.MessageActionPinMessage>`
            - :obj:`MessageActionScreenshotTaken <pyeitaa.raw.types.MessageActionScreenshotTaken>`
            - :obj:`MessageActionSecureValuesSent <pyeitaa.raw.types.MessageActionSecureValuesSent>`
            - :obj:`MessageActionSecureValuesSentMe <pyeitaa.raw.types.MessageActionSecureValuesSentMe>`
            - :obj:`MessageActionSetChatTheme <pyeitaa.raw.types.MessageActionSetChatTheme>`
            - :obj:`MessageActionSetMessagesTTL <pyeitaa.raw.types.MessageActionSetMessagesTTL>`
    """

    QUALNAME = "pyeitaa.raw.base.MessageAction"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
