from typing import Union
from pyeitaa import raw

ClientDHInnerData = Union[raw.types.ClientDHInnerData, raw.types.ClientDHInnerData]


# noinspection PyRedeclaration
class ClientDHInnerData:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ClientDHInnerData <pyeitaa.raw.types.ClientDHInnerData>`
            - :obj:`ClientDHInnerData <pyeitaa.raw.types.ClientDHInnerData>`
    """

    QUALNAME = "pyeitaa.raw.base.ClientDHInnerData"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
