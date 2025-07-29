from typing import Union
from pyeitaa import raw

MsgsStateInfo = Union[raw.types.MsgsStateInfo, raw.types.MsgsStateInfo]


# noinspection PyRedeclaration
class MsgsStateInfo:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`MsgsStateInfo <pyeitaa.raw.types.MsgsStateInfo>`
            - :obj:`MsgsStateInfo <pyeitaa.raw.types.MsgsStateInfo>`
    """

    QUALNAME = "pyeitaa.raw.base.MsgsStateInfo"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
