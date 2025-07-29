from typing import Union
from pyeitaa import raw

DestroySessionRes = Union[raw.types.DestroySessionNone, raw.types.DestroySessionNone, raw.types.DestroySessionOk, raw.types.DestroySessionOk]


# noinspection PyRedeclaration
class DestroySessionRes:
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`DestroySessionNone <pyeitaa.raw.types.DestroySessionNone>`
            - :obj:`DestroySessionNone <pyeitaa.raw.types.DestroySessionNone>`
            - :obj:`DestroySessionOk <pyeitaa.raw.types.DestroySessionOk>`
            - :obj:`DestroySessionOk <pyeitaa.raw.types.DestroySessionOk>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`DestroySession <pyeitaa.raw.functions.DestroySession>`
            - :obj:`DestroySession <pyeitaa.raw.functions.DestroySession>`
    """

    QUALNAME = "pyeitaa.raw.base.DestroySessionRes"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
