from typing import Union
from pyeitaa import raw

InputClientProxy = Union[raw.types.InputClientProxy]


# noinspection PyRedeclaration
class InputClientProxy:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputClientProxy <pyeitaa.raw.types.InputClientProxy>`
    """

    QUALNAME = "pyeitaa.raw.base.InputClientProxy"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
