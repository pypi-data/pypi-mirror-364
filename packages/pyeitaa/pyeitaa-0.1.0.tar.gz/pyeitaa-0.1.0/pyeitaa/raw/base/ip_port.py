from typing import Union
from pyeitaa import raw

IpPort = Union[raw.types.IpPort, raw.types.IpPortSecret]


# noinspection PyRedeclaration
class IpPort:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`IpPort <pyeitaa.raw.types.IpPort>`
            - :obj:`IpPortSecret <pyeitaa.raw.types.IpPortSecret>`
    """

    QUALNAME = "pyeitaa.raw.base.IpPort"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
