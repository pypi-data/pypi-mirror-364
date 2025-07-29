from typing import Union
from pyeitaa import raw

StatsAbsValueAndPrev = Union[raw.types.StatsAbsValueAndPrev]


# noinspection PyRedeclaration
class StatsAbsValueAndPrev:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`StatsAbsValueAndPrev <pyeitaa.raw.types.StatsAbsValueAndPrev>`
    """

    QUALNAME = "pyeitaa.raw.base.StatsAbsValueAndPrev"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
