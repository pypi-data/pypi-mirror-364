from typing import Union
from pyeitaa import raw

File = Union[raw.types.upload.File, raw.types.upload.FileCdnRedirect]


# noinspection PyRedeclaration
class File:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`upload.File <pyeitaa.raw.types.upload.File>`
            - :obj:`upload.FileCdnRedirect <pyeitaa.raw.types.upload.FileCdnRedirect>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`upload.GetFile <pyeitaa.raw.functions.upload.GetFile>`
            - :obj:`upload.GetFile2 <pyeitaa.raw.functions.upload.GetFile2>`
    """

    QUALNAME = "pyeitaa.raw.base.upload.File"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
