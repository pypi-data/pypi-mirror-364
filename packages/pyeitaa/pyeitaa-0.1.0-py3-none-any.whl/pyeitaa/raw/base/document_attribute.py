from typing import Union
from pyeitaa import raw

DocumentAttribute = Union[raw.types.DocumentAttributeAnimated, raw.types.DocumentAttributeAudio, raw.types.DocumentAttributeFilename, raw.types.DocumentAttributeHasStickers, raw.types.DocumentAttributeImageSize, raw.types.DocumentAttributeSticker, raw.types.DocumentAttributeVideo]


# noinspection PyRedeclaration
class DocumentAttribute:
    """This base type has 7 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`DocumentAttributeAnimated <pyeitaa.raw.types.DocumentAttributeAnimated>`
            - :obj:`DocumentAttributeAudio <pyeitaa.raw.types.DocumentAttributeAudio>`
            - :obj:`DocumentAttributeFilename <pyeitaa.raw.types.DocumentAttributeFilename>`
            - :obj:`DocumentAttributeHasStickers <pyeitaa.raw.types.DocumentAttributeHasStickers>`
            - :obj:`DocumentAttributeImageSize <pyeitaa.raw.types.DocumentAttributeImageSize>`
            - :obj:`DocumentAttributeSticker <pyeitaa.raw.types.DocumentAttributeSticker>`
            - :obj:`DocumentAttributeVideo <pyeitaa.raw.types.DocumentAttributeVideo>`
    """

    QUALNAME = "pyeitaa.raw.base.DocumentAttribute"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
