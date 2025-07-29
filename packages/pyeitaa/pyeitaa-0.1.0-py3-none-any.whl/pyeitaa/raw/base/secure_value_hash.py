from typing import Union
from pyeitaa import raw

SecureValueHash = Union[raw.types.SecureValueHash]


# noinspection PyRedeclaration
class SecureValueHash:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`SecureValueHash <pyeitaa.raw.types.SecureValueHash>`
    """

    QUALNAME = "pyeitaa.raw.base.SecureValueHash"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
