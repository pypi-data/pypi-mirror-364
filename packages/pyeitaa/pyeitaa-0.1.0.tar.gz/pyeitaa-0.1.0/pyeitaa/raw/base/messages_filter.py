from typing import Union
from pyeitaa import raw

MessagesFilter = Union[raw.types.InputMessagesFilterChatPhotos, raw.types.InputMessagesFilterContacts, raw.types.InputMessagesFilterDocument, raw.types.InputMessagesFilterEmpty, raw.types.InputMessagesFilterGeo, raw.types.InputMessagesFilterGif, raw.types.InputMessagesFilterMusic, raw.types.InputMessagesFilterMyMentions, raw.types.InputMessagesFilterPhoneCalls, raw.types.InputMessagesFilterPhotoVideo, raw.types.InputMessagesFilterPhotos, raw.types.InputMessagesFilterPinned, raw.types.InputMessagesFilterRoundVideo, raw.types.InputMessagesFilterRoundVoice, raw.types.InputMessagesFilterUrl, raw.types.InputMessagesFilterVideo, raw.types.InputMessagesFilterVoice]


# noinspection PyRedeclaration
class MessagesFilter:
    """This base type has 17 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputMessagesFilterChatPhotos <pyeitaa.raw.types.InputMessagesFilterChatPhotos>`
            - :obj:`InputMessagesFilterContacts <pyeitaa.raw.types.InputMessagesFilterContacts>`
            - :obj:`InputMessagesFilterDocument <pyeitaa.raw.types.InputMessagesFilterDocument>`
            - :obj:`InputMessagesFilterEmpty <pyeitaa.raw.types.InputMessagesFilterEmpty>`
            - :obj:`InputMessagesFilterGeo <pyeitaa.raw.types.InputMessagesFilterGeo>`
            - :obj:`InputMessagesFilterGif <pyeitaa.raw.types.InputMessagesFilterGif>`
            - :obj:`InputMessagesFilterMusic <pyeitaa.raw.types.InputMessagesFilterMusic>`
            - :obj:`InputMessagesFilterMyMentions <pyeitaa.raw.types.InputMessagesFilterMyMentions>`
            - :obj:`InputMessagesFilterPhoneCalls <pyeitaa.raw.types.InputMessagesFilterPhoneCalls>`
            - :obj:`InputMessagesFilterPhotoVideo <pyeitaa.raw.types.InputMessagesFilterPhotoVideo>`
            - :obj:`InputMessagesFilterPhotos <pyeitaa.raw.types.InputMessagesFilterPhotos>`
            - :obj:`InputMessagesFilterPinned <pyeitaa.raw.types.InputMessagesFilterPinned>`
            - :obj:`InputMessagesFilterRoundVideo <pyeitaa.raw.types.InputMessagesFilterRoundVideo>`
            - :obj:`InputMessagesFilterRoundVoice <pyeitaa.raw.types.InputMessagesFilterRoundVoice>`
            - :obj:`InputMessagesFilterUrl <pyeitaa.raw.types.InputMessagesFilterUrl>`
            - :obj:`InputMessagesFilterVideo <pyeitaa.raw.types.InputMessagesFilterVideo>`
            - :obj:`InputMessagesFilterVoice <pyeitaa.raw.types.InputMessagesFilterVoice>`
    """

    QUALNAME = "pyeitaa.raw.base.MessagesFilter"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
