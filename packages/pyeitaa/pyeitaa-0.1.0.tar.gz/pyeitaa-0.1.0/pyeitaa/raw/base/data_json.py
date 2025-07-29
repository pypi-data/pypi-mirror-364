from typing import Union
from pyeitaa import raw

DataJSON = Union[raw.types.DataJSON]


# noinspection PyRedeclaration
class DataJSON:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`DataJSON <pyeitaa.raw.types.DataJSON>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`bots.SendCustomRequest <pyeitaa.raw.functions.bots.SendCustomRequest>`
            - :obj:`phone.GetCallConfig <pyeitaa.raw.functions.phone.GetCallConfig>`
    """

    QUALNAME = "pyeitaa.raw.base.DataJSON"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
