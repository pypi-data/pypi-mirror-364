from typing import Union
from pyeitaa import raw

InputAppEvent = Union[raw.types.InputAppEvent]


# noinspection PyRedeclaration
class InputAppEvent:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputAppEvent <pyeitaa.raw.types.InputAppEvent>`
    """

    QUALNAME = "pyeitaa.raw.base.InputAppEvent"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
