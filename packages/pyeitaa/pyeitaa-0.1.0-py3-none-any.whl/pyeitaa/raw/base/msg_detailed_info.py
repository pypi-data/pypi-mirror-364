from typing import Union
from pyeitaa import raw

MsgDetailedInfo = Union[raw.types.MsgDetailedInfo, raw.types.MsgDetailedInfo, raw.types.MsgNewDetailedInfo, raw.types.MsgNewDetailedInfo]


# noinspection PyRedeclaration
class MsgDetailedInfo:
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`MsgDetailedInfo <pyeitaa.raw.types.MsgDetailedInfo>`
            - :obj:`MsgDetailedInfo <pyeitaa.raw.types.MsgDetailedInfo>`
            - :obj:`MsgNewDetailedInfo <pyeitaa.raw.types.MsgNewDetailedInfo>`
            - :obj:`MsgNewDetailedInfo <pyeitaa.raw.types.MsgNewDetailedInfo>`
    """

    QUALNAME = "pyeitaa.raw.base.MsgDetailedInfo"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
