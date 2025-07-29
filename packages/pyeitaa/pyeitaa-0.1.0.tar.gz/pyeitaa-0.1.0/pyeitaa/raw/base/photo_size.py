from typing import Union
from pyeitaa import raw

PhotoSize = Union[raw.types.PhotoCachedSize, raw.types.PhotoCachedSize, raw.types.PhotoPathSize, raw.types.PhotoSize, raw.types.PhotoSize, raw.types.PhotoSizeEmpty, raw.types.PhotoSizeProgressive, raw.types.PhotoStrippedSize]


# noinspection PyRedeclaration
class PhotoSize:
    """This base type has 8 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PhotoCachedSize <pyeitaa.raw.types.PhotoCachedSize>`
            - :obj:`PhotoCachedSize <pyeitaa.raw.types.PhotoCachedSize>`
            - :obj:`PhotoPathSize <pyeitaa.raw.types.PhotoPathSize>`
            - :obj:`PhotoSize <pyeitaa.raw.types.PhotoSize>`
            - :obj:`PhotoSize <pyeitaa.raw.types.PhotoSize>`
            - :obj:`PhotoSizeEmpty <pyeitaa.raw.types.PhotoSizeEmpty>`
            - :obj:`PhotoSizeProgressive <pyeitaa.raw.types.PhotoSizeProgressive>`
            - :obj:`PhotoStrippedSize <pyeitaa.raw.types.PhotoStrippedSize>`
    """

    QUALNAME = "pyeitaa.raw.base.PhotoSize"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
