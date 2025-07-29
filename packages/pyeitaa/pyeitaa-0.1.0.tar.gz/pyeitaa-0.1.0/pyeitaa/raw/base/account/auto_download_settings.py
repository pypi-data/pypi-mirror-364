from typing import Union
from pyeitaa import raw

AutoDownloadSettings = Union[raw.types.account.AutoDownloadSettings]


# noinspection PyRedeclaration
class AutoDownloadSettings:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`account.AutoDownloadSettings <pyeitaa.raw.types.account.AutoDownloadSettings>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetAutoDownloadSettings <pyeitaa.raw.functions.account.GetAutoDownloadSettings>`
    """

    QUALNAME = "pyeitaa.raw.base.account.AutoDownloadSettings"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
