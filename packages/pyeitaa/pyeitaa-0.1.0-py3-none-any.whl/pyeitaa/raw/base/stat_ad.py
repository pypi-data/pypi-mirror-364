from typing import Union
from pyeitaa import raw

StatAd = Union[raw.types.StatAd]


# noinspection PyRedeclaration
class StatAd:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`StatAd <pyeitaa.raw.types.StatAd>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`StatAd <pyeitaa.raw.functions.StatAd>`
    """

    QUALNAME = "pyeitaa.raw.base.StatAd"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
