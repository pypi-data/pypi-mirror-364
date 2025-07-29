from typing import Union
from pyeitaa import raw

AccessPointRule = Union[raw.types.AccessPointRule]


# noinspection PyRedeclaration
class AccessPointRule:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`AccessPointRule <pyeitaa.raw.types.AccessPointRule>`
    """

    QUALNAME = "pyeitaa.raw.base.AccessPointRule"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
