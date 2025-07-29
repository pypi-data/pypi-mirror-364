from typing import Union
from pyeitaa import raw

PostAddress = Union[raw.types.PostAddress]


# noinspection PyRedeclaration
class PostAddress:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PostAddress <pyeitaa.raw.types.PostAddress>`
    """

    QUALNAME = "pyeitaa.raw.base.PostAddress"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
