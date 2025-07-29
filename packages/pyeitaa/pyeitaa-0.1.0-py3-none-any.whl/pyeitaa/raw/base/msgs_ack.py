from typing import Union
from pyeitaa import raw

MsgsAck = Union[raw.types.MsgsAck, raw.types.MsgsAck]


# noinspection PyRedeclaration
class MsgsAck:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`MsgsAck <pyeitaa.raw.types.MsgsAck>`
            - :obj:`MsgsAck <pyeitaa.raw.types.MsgsAck>`
    """

    QUALNAME = "pyeitaa.raw.base.MsgsAck"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
