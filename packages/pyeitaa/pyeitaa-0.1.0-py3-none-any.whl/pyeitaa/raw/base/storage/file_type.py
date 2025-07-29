from typing import Union
from pyeitaa import raw

FileType = Union[raw.types.storage.FileGif, raw.types.storage.FileJpeg, raw.types.storage.FileMov, raw.types.storage.FileMp3, raw.types.storage.FileMp4, raw.types.storage.FilePartial, raw.types.storage.FilePdf, raw.types.storage.FilePng, raw.types.storage.FileUnknown, raw.types.storage.FileWebp]


# noinspection PyRedeclaration
class FileType:
    """This base type has 10 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`storage.FileGif <pyeitaa.raw.types.storage.FileGif>`
            - :obj:`storage.FileJpeg <pyeitaa.raw.types.storage.FileJpeg>`
            - :obj:`storage.FileMov <pyeitaa.raw.types.storage.FileMov>`
            - :obj:`storage.FileMp3 <pyeitaa.raw.types.storage.FileMp3>`
            - :obj:`storage.FileMp4 <pyeitaa.raw.types.storage.FileMp4>`
            - :obj:`storage.FilePartial <pyeitaa.raw.types.storage.FilePartial>`
            - :obj:`storage.FilePdf <pyeitaa.raw.types.storage.FilePdf>`
            - :obj:`storage.FilePng <pyeitaa.raw.types.storage.FilePng>`
            - :obj:`storage.FileUnknown <pyeitaa.raw.types.storage.FileUnknown>`
            - :obj:`storage.FileWebp <pyeitaa.raw.types.storage.FileWebp>`
    """

    QUALNAME = "pyeitaa.raw.base.storage.FileType"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
