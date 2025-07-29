from typing import Union
from pyeitaa import raw

PhoneConnection = Union[raw.types.PhoneConnection, raw.types.PhoneConnectionWebrtc]


# noinspection PyRedeclaration
class PhoneConnection:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PhoneConnection <pyeitaa.raw.types.PhoneConnection>`
            - :obj:`PhoneConnectionWebrtc <pyeitaa.raw.types.PhoneConnectionWebrtc>`
    """

    QUALNAME = "pyeitaa.raw.base.PhoneConnection"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
