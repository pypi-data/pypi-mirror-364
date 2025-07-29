from typing import Union
from pyeitaa import raw

StatsURL = Union[raw.types.StatsURL]


# noinspection PyRedeclaration
class StatsURL:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`StatsURL <pyeitaa.raw.types.StatsURL>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetStatsURL <pyeitaa.raw.functions.messages.GetStatsURL>`
    """

    QUALNAME = "pyeitaa.raw.base.StatsURL"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
