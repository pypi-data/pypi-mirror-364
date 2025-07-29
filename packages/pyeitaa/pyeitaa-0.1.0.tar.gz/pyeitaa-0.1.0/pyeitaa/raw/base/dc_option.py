from typing import Union
from pyeitaa import raw

DcOption = Union[raw.types.DcOption]


# noinspection PyRedeclaration
class DcOption:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`DcOption <pyeitaa.raw.types.DcOption>`
    """

    QUALNAME = "pyeitaa.raw.base.DcOption"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
