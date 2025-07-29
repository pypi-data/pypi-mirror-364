from typing import Union
from pyeitaa import raw

StatsDateRangeDays = Union[raw.types.StatsDateRangeDays]


# noinspection PyRedeclaration
class StatsDateRangeDays:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`StatsDateRangeDays <pyeitaa.raw.types.StatsDateRangeDays>`
    """

    QUALNAME = "pyeitaa.raw.base.StatsDateRangeDays"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
