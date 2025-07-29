from typing import Union
from pyeitaa import raw

StatsGroupTopPoster = Union[raw.types.StatsGroupTopPoster]


# noinspection PyRedeclaration
class StatsGroupTopPoster:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`StatsGroupTopPoster <pyeitaa.raw.types.StatsGroupTopPoster>`
    """

    QUALNAME = "pyeitaa.raw.base.StatsGroupTopPoster"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
