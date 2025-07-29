from typing import Union
from pyeitaa import raw

InputWebDocument = Union[raw.types.InputWebDocument]


# noinspection PyRedeclaration
class InputWebDocument:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputWebDocument <pyeitaa.raw.types.InputWebDocument>`
    """

    QUALNAME = "pyeitaa.raw.base.InputWebDocument"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
