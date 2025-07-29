from typing import Union
from pyeitaa import raw

ChannelAdminLogEventAction = Union[raw.types.ChannelAdminLogEventActionChangeAbout, raw.types.ChannelAdminLogEventActionChangeHistoryTTL, raw.types.ChannelAdminLogEventActionChangeLinkedChat, raw.types.ChannelAdminLogEventActionChangeLocation, raw.types.ChannelAdminLogEventActionChangePhoto, raw.types.ChannelAdminLogEventActionChangeStickerSet, raw.types.ChannelAdminLogEventActionChangeTheme, raw.types.ChannelAdminLogEventActionChangeTitle, raw.types.ChannelAdminLogEventActionChangeUsername, raw.types.ChannelAdminLogEventActionDefaultBannedRights, raw.types.ChannelAdminLogEventActionDeleteMessage, raw.types.ChannelAdminLogEventActionDiscardGroupCall, raw.types.ChannelAdminLogEventActionEditMessage, raw.types.ChannelAdminLogEventActionExportedInviteDelete, raw.types.ChannelAdminLogEventActionExportedInviteEdit, raw.types.ChannelAdminLogEventActionExportedInviteRevoke, raw.types.ChannelAdminLogEventActionParticipantInvite, raw.types.ChannelAdminLogEventActionParticipantJoin, raw.types.ChannelAdminLogEventActionParticipantJoinByInvite, raw.types.ChannelAdminLogEventActionParticipantLeave, raw.types.ChannelAdminLogEventActionParticipantMute, raw.types.ChannelAdminLogEventActionParticipantToggleAdmin, raw.types.ChannelAdminLogEventActionParticipantToggleBan, raw.types.ChannelAdminLogEventActionParticipantUnmute, raw.types.ChannelAdminLogEventActionParticipantVolume, raw.types.ChannelAdminLogEventActionStartGroupCall, raw.types.ChannelAdminLogEventActionStopPoll, raw.types.ChannelAdminLogEventActionToggleGroupCallSetting, raw.types.ChannelAdminLogEventActionToggleInvites, raw.types.ChannelAdminLogEventActionTogglePreHistoryHidden, raw.types.ChannelAdminLogEventActionToggleSignatures, raw.types.ChannelAdminLogEventActionToggleSlowMode, raw.types.ChannelAdminLogEventActionUpdatePinned]


# noinspection PyRedeclaration
class ChannelAdminLogEventAction:
    """This base type has 33 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ChannelAdminLogEventActionChangeAbout <pyeitaa.raw.types.ChannelAdminLogEventActionChangeAbout>`
            - :obj:`ChannelAdminLogEventActionChangeHistoryTTL <pyeitaa.raw.types.ChannelAdminLogEventActionChangeHistoryTTL>`
            - :obj:`ChannelAdminLogEventActionChangeLinkedChat <pyeitaa.raw.types.ChannelAdminLogEventActionChangeLinkedChat>`
            - :obj:`ChannelAdminLogEventActionChangeLocation <pyeitaa.raw.types.ChannelAdminLogEventActionChangeLocation>`
            - :obj:`ChannelAdminLogEventActionChangePhoto <pyeitaa.raw.types.ChannelAdminLogEventActionChangePhoto>`
            - :obj:`ChannelAdminLogEventActionChangeStickerSet <pyeitaa.raw.types.ChannelAdminLogEventActionChangeStickerSet>`
            - :obj:`ChannelAdminLogEventActionChangeTheme <pyeitaa.raw.types.ChannelAdminLogEventActionChangeTheme>`
            - :obj:`ChannelAdminLogEventActionChangeTitle <pyeitaa.raw.types.ChannelAdminLogEventActionChangeTitle>`
            - :obj:`ChannelAdminLogEventActionChangeUsername <pyeitaa.raw.types.ChannelAdminLogEventActionChangeUsername>`
            - :obj:`ChannelAdminLogEventActionDefaultBannedRights <pyeitaa.raw.types.ChannelAdminLogEventActionDefaultBannedRights>`
            - :obj:`ChannelAdminLogEventActionDeleteMessage <pyeitaa.raw.types.ChannelAdminLogEventActionDeleteMessage>`
            - :obj:`ChannelAdminLogEventActionDiscardGroupCall <pyeitaa.raw.types.ChannelAdminLogEventActionDiscardGroupCall>`
            - :obj:`ChannelAdminLogEventActionEditMessage <pyeitaa.raw.types.ChannelAdminLogEventActionEditMessage>`
            - :obj:`ChannelAdminLogEventActionExportedInviteDelete <pyeitaa.raw.types.ChannelAdminLogEventActionExportedInviteDelete>`
            - :obj:`ChannelAdminLogEventActionExportedInviteEdit <pyeitaa.raw.types.ChannelAdminLogEventActionExportedInviteEdit>`
            - :obj:`ChannelAdminLogEventActionExportedInviteRevoke <pyeitaa.raw.types.ChannelAdminLogEventActionExportedInviteRevoke>`
            - :obj:`ChannelAdminLogEventActionParticipantInvite <pyeitaa.raw.types.ChannelAdminLogEventActionParticipantInvite>`
            - :obj:`ChannelAdminLogEventActionParticipantJoin <pyeitaa.raw.types.ChannelAdminLogEventActionParticipantJoin>`
            - :obj:`ChannelAdminLogEventActionParticipantJoinByInvite <pyeitaa.raw.types.ChannelAdminLogEventActionParticipantJoinByInvite>`
            - :obj:`ChannelAdminLogEventActionParticipantLeave <pyeitaa.raw.types.ChannelAdminLogEventActionParticipantLeave>`
            - :obj:`ChannelAdminLogEventActionParticipantMute <pyeitaa.raw.types.ChannelAdminLogEventActionParticipantMute>`
            - :obj:`ChannelAdminLogEventActionParticipantToggleAdmin <pyeitaa.raw.types.ChannelAdminLogEventActionParticipantToggleAdmin>`
            - :obj:`ChannelAdminLogEventActionParticipantToggleBan <pyeitaa.raw.types.ChannelAdminLogEventActionParticipantToggleBan>`
            - :obj:`ChannelAdminLogEventActionParticipantUnmute <pyeitaa.raw.types.ChannelAdminLogEventActionParticipantUnmute>`
            - :obj:`ChannelAdminLogEventActionParticipantVolume <pyeitaa.raw.types.ChannelAdminLogEventActionParticipantVolume>`
            - :obj:`ChannelAdminLogEventActionStartGroupCall <pyeitaa.raw.types.ChannelAdminLogEventActionStartGroupCall>`
            - :obj:`ChannelAdminLogEventActionStopPoll <pyeitaa.raw.types.ChannelAdminLogEventActionStopPoll>`
            - :obj:`ChannelAdminLogEventActionToggleGroupCallSetting <pyeitaa.raw.types.ChannelAdminLogEventActionToggleGroupCallSetting>`
            - :obj:`ChannelAdminLogEventActionToggleInvites <pyeitaa.raw.types.ChannelAdminLogEventActionToggleInvites>`
            - :obj:`ChannelAdminLogEventActionTogglePreHistoryHidden <pyeitaa.raw.types.ChannelAdminLogEventActionTogglePreHistoryHidden>`
            - :obj:`ChannelAdminLogEventActionToggleSignatures <pyeitaa.raw.types.ChannelAdminLogEventActionToggleSignatures>`
            - :obj:`ChannelAdminLogEventActionToggleSlowMode <pyeitaa.raw.types.ChannelAdminLogEventActionToggleSlowMode>`
            - :obj:`ChannelAdminLogEventActionUpdatePinned <pyeitaa.raw.types.ChannelAdminLogEventActionUpdatePinned>`
    """

    QUALNAME = "pyeitaa.raw.base.ChannelAdminLogEventAction"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
