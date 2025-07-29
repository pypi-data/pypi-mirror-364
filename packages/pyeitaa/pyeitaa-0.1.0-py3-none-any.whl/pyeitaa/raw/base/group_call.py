from typing import Union
from pyeitaa import raw

GroupCall = Union[raw.types.GroupCall, raw.types.GroupCallDiscarded]


# noinspection PyRedeclaration
class GroupCall:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`GroupCall <pyeitaa.raw.types.GroupCall>`
            - :obj:`GroupCallDiscarded <pyeitaa.raw.types.GroupCallDiscarded>`
    """

    QUALNAME = "pyeitaa.raw.base.GroupCall"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
