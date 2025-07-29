from typing import Union
from pyeitaa import raw

ConfigSimple = Union[raw.types.help.ConfigSimple]


# noinspection PyRedeclaration
class ConfigSimple:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`help.ConfigSimple <pyeitaa.raw.types.help.ConfigSimple>`
    """

    QUALNAME = "pyeitaa.raw.base.help.ConfigSimple"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
