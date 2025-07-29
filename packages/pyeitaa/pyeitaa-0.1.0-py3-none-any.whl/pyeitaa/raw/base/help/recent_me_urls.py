from typing import Union
from pyeitaa import raw

RecentMeUrls = Union[raw.types.help.RecentMeUrls]


# noinspection PyRedeclaration
class RecentMeUrls:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`help.RecentMeUrls <pyeitaa.raw.types.help.RecentMeUrls>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetRecentMeUrls <pyeitaa.raw.functions.help.GetRecentMeUrls>`
    """

    QUALNAME = "pyeitaa.raw.base.help.RecentMeUrls"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
