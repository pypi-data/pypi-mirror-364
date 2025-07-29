from typing import Union
from pyeitaa import raw

InputMedia = Union[raw.types.InputMediaContact, raw.types.InputMediaDice, raw.types.InputMediaDocument, raw.types.InputMediaDocumentExternal, raw.types.InputMediaEmpty, raw.types.InputMediaGame, raw.types.InputMediaGeoLive, raw.types.InputMediaGeoPoint, raw.types.InputMediaInvoice, raw.types.InputMediaPhoto, raw.types.InputMediaPhotoExternal, raw.types.InputMediaPoll, raw.types.InputMediaUploadedDocument, raw.types.InputMediaUploadedPhoto, raw.types.InputMediaVenue]


# noinspection PyRedeclaration
class InputMedia:
    """This base type has 15 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputMediaContact <pyeitaa.raw.types.InputMediaContact>`
            - :obj:`InputMediaDice <pyeitaa.raw.types.InputMediaDice>`
            - :obj:`InputMediaDocument <pyeitaa.raw.types.InputMediaDocument>`
            - :obj:`InputMediaDocumentExternal <pyeitaa.raw.types.InputMediaDocumentExternal>`
            - :obj:`InputMediaEmpty <pyeitaa.raw.types.InputMediaEmpty>`
            - :obj:`InputMediaGame <pyeitaa.raw.types.InputMediaGame>`
            - :obj:`InputMediaGeoLive <pyeitaa.raw.types.InputMediaGeoLive>`
            - :obj:`InputMediaGeoPoint <pyeitaa.raw.types.InputMediaGeoPoint>`
            - :obj:`InputMediaInvoice <pyeitaa.raw.types.InputMediaInvoice>`
            - :obj:`InputMediaPhoto <pyeitaa.raw.types.InputMediaPhoto>`
            - :obj:`InputMediaPhotoExternal <pyeitaa.raw.types.InputMediaPhotoExternal>`
            - :obj:`InputMediaPoll <pyeitaa.raw.types.InputMediaPoll>`
            - :obj:`InputMediaUploadedDocument <pyeitaa.raw.types.InputMediaUploadedDocument>`
            - :obj:`InputMediaUploadedPhoto <pyeitaa.raw.types.InputMediaUploadedPhoto>`
            - :obj:`InputMediaVenue <pyeitaa.raw.types.InputMediaVenue>`
    """

    QUALNAME = "pyeitaa.raw.base.InputMedia"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
