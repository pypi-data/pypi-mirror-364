from typing import Union
from pyeitaa import raw

DialogFilter = Union[raw.types.DialogFilter]


# noinspection PyRedeclaration
class DialogFilter:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`DialogFilter <pyeitaa.raw.types.DialogFilter>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetDialogFilters <pyeitaa.raw.functions.messages.GetDialogFilters>`
    """

    QUALNAME = "pyeitaa.raw.base.DialogFilter"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
