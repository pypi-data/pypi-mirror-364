from typing import Union
from pyeitaa import raw

AdminLogResults = Union[raw.types.channels.AdminLogResults]


# noinspection PyRedeclaration
class AdminLogResults:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`channels.AdminLogResults <pyeitaa.raw.types.channels.AdminLogResults>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`channels.GetAdminLog <pyeitaa.raw.functions.channels.GetAdminLog>`
    """

    QUALNAME = "pyeitaa.raw.base.channels.AdminLogResults"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
