from typing import Union
from pyeitaa import raw

ServerDHInnerData = Union[raw.types.ServerDHInnerData, raw.types.ServerDHInnerData]


# noinspection PyRedeclaration
class ServerDHInnerData:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ServerDHInnerData <pyeitaa.raw.types.ServerDHInnerData>`
            - :obj:`ServerDHInnerData <pyeitaa.raw.types.ServerDHInnerData>`
    """

    QUALNAME = "pyeitaa.raw.base.ServerDHInnerData"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
