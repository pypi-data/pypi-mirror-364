from typing import Union
from pyeitaa import raw

MessageMedia = Union[raw.types.MessageMediaContact, raw.types.MessageMediaDice, raw.types.MessageMediaDocument, raw.types.MessageMediaEmpty, raw.types.MessageMediaGame, raw.types.MessageMediaGeo, raw.types.MessageMediaGeoLive, raw.types.MessageMediaInvoice, raw.types.MessageMediaLiveStream, raw.types.MessageMediaPhoto, raw.types.MessageMediaPoll, raw.types.MessageMediaUnsupported, raw.types.MessageMediaVenue, raw.types.MessageMediaWebPage]


# noinspection PyRedeclaration
class MessageMedia:
    """This base type has 14 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`MessageMediaContact <pyeitaa.raw.types.MessageMediaContact>`
            - :obj:`MessageMediaDice <pyeitaa.raw.types.MessageMediaDice>`
            - :obj:`MessageMediaDocument <pyeitaa.raw.types.MessageMediaDocument>`
            - :obj:`MessageMediaEmpty <pyeitaa.raw.types.MessageMediaEmpty>`
            - :obj:`MessageMediaGame <pyeitaa.raw.types.MessageMediaGame>`
            - :obj:`MessageMediaGeo <pyeitaa.raw.types.MessageMediaGeo>`
            - :obj:`MessageMediaGeoLive <pyeitaa.raw.types.MessageMediaGeoLive>`
            - :obj:`MessageMediaInvoice <pyeitaa.raw.types.MessageMediaInvoice>`
            - :obj:`MessageMediaLiveStream <pyeitaa.raw.types.MessageMediaLiveStream>`
            - :obj:`MessageMediaPhoto <pyeitaa.raw.types.MessageMediaPhoto>`
            - :obj:`MessageMediaPoll <pyeitaa.raw.types.MessageMediaPoll>`
            - :obj:`MessageMediaUnsupported <pyeitaa.raw.types.MessageMediaUnsupported>`
            - :obj:`MessageMediaVenue <pyeitaa.raw.types.MessageMediaVenue>`
            - :obj:`MessageMediaWebPage <pyeitaa.raw.types.MessageMediaWebPage>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPagePreview <pyeitaa.raw.functions.messages.GetWebPagePreview>`
            - :obj:`messages.UploadMedia <pyeitaa.raw.functions.messages.UploadMedia>`
            - :obj:`messages.UploadImportedMedia <pyeitaa.raw.functions.messages.UploadImportedMedia>`
    """

    QUALNAME = "pyeitaa.raw.base.MessageMedia"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
