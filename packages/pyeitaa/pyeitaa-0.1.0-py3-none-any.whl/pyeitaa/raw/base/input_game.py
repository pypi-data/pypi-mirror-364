from typing import Union
from pyeitaa import raw

InputGame = Union[raw.types.InputGameID, raw.types.InputGameShortName]


# noinspection PyRedeclaration
class InputGame:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputGameID <pyeitaa.raw.types.InputGameID>`
            - :obj:`InputGameShortName <pyeitaa.raw.types.InputGameShortName>`
    """

    QUALNAME = "pyeitaa.raw.base.InputGame"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
