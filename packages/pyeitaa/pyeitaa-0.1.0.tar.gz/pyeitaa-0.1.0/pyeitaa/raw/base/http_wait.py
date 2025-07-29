from typing import Union
from pyeitaa import raw

HttpWait = Union[raw.types.HttpWait]


# noinspection PyRedeclaration
class HttpWait:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`HttpWait <pyeitaa.raw.types.HttpWait>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`HttpWait <pyeitaa.raw.functions.HttpWait>`
    """

    QUALNAME = "pyeitaa.raw.base.HttpWait"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
