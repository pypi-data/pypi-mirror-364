from typing import Union
from pyeitaa import raw

CodeSettings = Union[raw.types.CodeSettings]


# noinspection PyRedeclaration
class CodeSettings:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`CodeSettings <pyeitaa.raw.types.CodeSettings>`
    """

    QUALNAME = "pyeitaa.raw.base.CodeSettings"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
