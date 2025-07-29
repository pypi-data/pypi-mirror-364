from typing import Union
from pyeitaa import raw

Config = Union[raw.types.Config]


# noinspection PyRedeclaration
class Config:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`Config <pyeitaa.raw.types.Config>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetConfig <pyeitaa.raw.functions.help.GetConfig>`
    """

    QUALNAME = "pyeitaa.raw.base.Config"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
