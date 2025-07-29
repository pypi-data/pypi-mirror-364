from typing import Union
from pyeitaa import raw

MsgsAllInfo = Union[raw.types.MsgsAllInfo, raw.types.MsgsAllInfo]


# noinspection PyRedeclaration
class MsgsAllInfo:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`MsgsAllInfo <pyeitaa.raw.types.MsgsAllInfo>`
            - :obj:`MsgsAllInfo <pyeitaa.raw.types.MsgsAllInfo>`
    """

    QUALNAME = "pyeitaa.raw.base.MsgsAllInfo"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
