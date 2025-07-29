from typing import Union
from pyeitaa import raw

SecurePlainData = Union[raw.types.SecurePlainEmail, raw.types.SecurePlainPhone]


# noinspection PyRedeclaration
class SecurePlainData:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`SecurePlainEmail <pyeitaa.raw.types.SecurePlainEmail>`
            - :obj:`SecurePlainPhone <pyeitaa.raw.types.SecurePlainPhone>`
    """

    QUALNAME = "pyeitaa.raw.base.SecurePlainData"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
