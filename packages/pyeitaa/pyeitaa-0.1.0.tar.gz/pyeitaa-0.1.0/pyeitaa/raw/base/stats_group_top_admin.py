from typing import Union
from pyeitaa import raw

StatsGroupTopAdmin = Union[raw.types.StatsGroupTopAdmin]


# noinspection PyRedeclaration
class StatsGroupTopAdmin:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`StatsGroupTopAdmin <pyeitaa.raw.types.StatsGroupTopAdmin>`
    """

    QUALNAME = "pyeitaa.raw.base.StatsGroupTopAdmin"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
