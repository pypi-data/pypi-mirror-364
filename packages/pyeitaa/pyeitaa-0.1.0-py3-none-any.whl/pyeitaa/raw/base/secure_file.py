from typing import Union
from pyeitaa import raw

SecureFile = Union[raw.types.SecureFile, raw.types.SecureFileEmpty]


# noinspection PyRedeclaration
class SecureFile:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`SecureFile <pyeitaa.raw.types.SecureFile>`
            - :obj:`SecureFileEmpty <pyeitaa.raw.types.SecureFileEmpty>`
    """

    QUALNAME = "pyeitaa.raw.base.SecureFile"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
