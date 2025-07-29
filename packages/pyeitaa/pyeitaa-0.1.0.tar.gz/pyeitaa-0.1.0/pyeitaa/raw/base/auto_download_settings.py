from typing import Union
from pyeitaa import raw

AutoDownloadSettings = Union[raw.types.AutoDownloadSettings]


# noinspection PyRedeclaration
class AutoDownloadSettings:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`AutoDownloadSettings <pyeitaa.raw.types.AutoDownloadSettings>`
    """

    QUALNAME = "pyeitaa.raw.base.AutoDownloadSettings"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
