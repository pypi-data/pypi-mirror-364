from typing import Union
from pyeitaa import raw

SecureRequiredType = Union[raw.types.SecureRequiredType, raw.types.SecureRequiredTypeOneOf]


# noinspection PyRedeclaration
class SecureRequiredType:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`SecureRequiredType <pyeitaa.raw.types.SecureRequiredType>`
            - :obj:`SecureRequiredTypeOneOf <pyeitaa.raw.types.SecureRequiredTypeOneOf>`
    """

    QUALNAME = "pyeitaa.raw.base.SecureRequiredType"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
