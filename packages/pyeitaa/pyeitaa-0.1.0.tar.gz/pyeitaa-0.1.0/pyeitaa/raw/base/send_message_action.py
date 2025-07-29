from typing import Union
from pyeitaa import raw

SendMessageAction = Union[raw.types.SendMessageCancelAction, raw.types.SendMessageChooseContactAction, raw.types.SendMessageChooseStickerAction, raw.types.SendMessageEmojiInteraction, raw.types.SendMessageEmojiInteractionSeen, raw.types.SendMessageGamePlayAction, raw.types.SendMessageGeoLocationAction, raw.types.SendMessageHistoryImportAction, raw.types.SendMessageRecordAudioAction, raw.types.SendMessageRecordRoundAction, raw.types.SendMessageRecordVideoAction, raw.types.SendMessageTypingAction, raw.types.SendMessageUploadAudioAction, raw.types.SendMessageUploadDocumentAction, raw.types.SendMessageUploadPhotoAction, raw.types.SendMessageUploadRoundAction, raw.types.SendMessageUploadVideoAction, raw.types.SpeakingInGroupCallAction]


# noinspection PyRedeclaration
class SendMessageAction:
    """This base type has 18 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`SendMessageCancelAction <pyeitaa.raw.types.SendMessageCancelAction>`
            - :obj:`SendMessageChooseContactAction <pyeitaa.raw.types.SendMessageChooseContactAction>`
            - :obj:`SendMessageChooseStickerAction <pyeitaa.raw.types.SendMessageChooseStickerAction>`
            - :obj:`SendMessageEmojiInteraction <pyeitaa.raw.types.SendMessageEmojiInteraction>`
            - :obj:`SendMessageEmojiInteractionSeen <pyeitaa.raw.types.SendMessageEmojiInteractionSeen>`
            - :obj:`SendMessageGamePlayAction <pyeitaa.raw.types.SendMessageGamePlayAction>`
            - :obj:`SendMessageGeoLocationAction <pyeitaa.raw.types.SendMessageGeoLocationAction>`
            - :obj:`SendMessageHistoryImportAction <pyeitaa.raw.types.SendMessageHistoryImportAction>`
            - :obj:`SendMessageRecordAudioAction <pyeitaa.raw.types.SendMessageRecordAudioAction>`
            - :obj:`SendMessageRecordRoundAction <pyeitaa.raw.types.SendMessageRecordRoundAction>`
            - :obj:`SendMessageRecordVideoAction <pyeitaa.raw.types.SendMessageRecordVideoAction>`
            - :obj:`SendMessageTypingAction <pyeitaa.raw.types.SendMessageTypingAction>`
            - :obj:`SendMessageUploadAudioAction <pyeitaa.raw.types.SendMessageUploadAudioAction>`
            - :obj:`SendMessageUploadDocumentAction <pyeitaa.raw.types.SendMessageUploadDocumentAction>`
            - :obj:`SendMessageUploadPhotoAction <pyeitaa.raw.types.SendMessageUploadPhotoAction>`
            - :obj:`SendMessageUploadRoundAction <pyeitaa.raw.types.SendMessageUploadRoundAction>`
            - :obj:`SendMessageUploadVideoAction <pyeitaa.raw.types.SendMessageUploadVideoAction>`
            - :obj:`SpeakingInGroupCallAction <pyeitaa.raw.types.SpeakingInGroupCallAction>`
    """

    QUALNAME = "pyeitaa.raw.base.SendMessageAction"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
