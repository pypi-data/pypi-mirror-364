from typing import Union
from pyeitaa import raw

InputUser = Union[raw.types.InputUser, raw.types.InputUserEmpty, raw.types.InputUserFromMessage, raw.types.InputUserSelf]


# noinspection PyRedeclaration
class InputUser:
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputUser <pyeitaa.raw.types.InputUser>`
            - :obj:`InputUserEmpty <pyeitaa.raw.types.InputUserEmpty>`
            - :obj:`InputUserFromMessage <pyeitaa.raw.types.InputUserFromMessage>`
            - :obj:`InputUserSelf <pyeitaa.raw.types.InputUserSelf>`
    """

    QUALNAME = "pyeitaa.raw.base.InputUser"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
