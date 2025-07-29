from typing import Union
from pyeitaa import raw

SecureData = Union[raw.types.SecureData]


# noinspection PyRedeclaration
class SecureData:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`SecureData <pyeitaa.raw.types.SecureData>`
    """

    QUALNAME = "pyeitaa.raw.base.SecureData"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
