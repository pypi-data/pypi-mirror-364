from typing import Union
from pyeitaa import raw

WebAuthorization = Union[raw.types.WebAuthorization]


# noinspection PyRedeclaration
class WebAuthorization:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`WebAuthorization <pyeitaa.raw.types.WebAuthorization>`
    """

    QUALNAME = "pyeitaa.raw.base.WebAuthorization"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
