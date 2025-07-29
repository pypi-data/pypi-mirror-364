from typing import Union
from pyeitaa import raw

CdnFile = Union[raw.types.upload.CdnFile, raw.types.upload.CdnFileReuploadNeeded]


# noinspection PyRedeclaration
class CdnFile:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`upload.CdnFile <pyeitaa.raw.types.upload.CdnFile>`
            - :obj:`upload.CdnFileReuploadNeeded <pyeitaa.raw.types.upload.CdnFileReuploadNeeded>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`upload.GetCdnFile <pyeitaa.raw.functions.upload.GetCdnFile>`
    """

    QUALNAME = "pyeitaa.raw.base.upload.CdnFile"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
