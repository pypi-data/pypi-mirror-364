from typing import Union
from pyeitaa import raw

FileHash = Union[raw.types.FileHash]


# noinspection PyRedeclaration
class FileHash:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`FileHash <pyeitaa.raw.types.FileHash>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`upload.ReuploadCdnFile <pyeitaa.raw.functions.upload.ReuploadCdnFile>`
            - :obj:`upload.GetCdnFileHashes <pyeitaa.raw.functions.upload.GetCdnFileHashes>`
            - :obj:`upload.GetFileHashes <pyeitaa.raw.functions.upload.GetFileHashes>`
    """

    QUALNAME = "pyeitaa.raw.base.FileHash"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
