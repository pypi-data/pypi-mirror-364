from typing import Union
from pyeitaa import raw

InputSingleMedia = Union[raw.types.InputSingleMedia]


# noinspection PyRedeclaration
class InputSingleMedia:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputSingleMedia <pyeitaa.raw.types.InputSingleMedia>`
    """

    QUALNAME = "pyeitaa.raw.base.InputSingleMedia"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
