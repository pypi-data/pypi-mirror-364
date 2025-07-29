from typing import Union
from pyeitaa import raw

StatsGraph = Union[raw.types.StatsGraph, raw.types.StatsGraphAsync, raw.types.StatsGraphError]


# noinspection PyRedeclaration
class StatsGraph:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`StatsGraph <pyeitaa.raw.types.StatsGraph>`
            - :obj:`StatsGraphAsync <pyeitaa.raw.types.StatsGraphAsync>`
            - :obj:`StatsGraphError <pyeitaa.raw.types.StatsGraphError>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`stats.LoadAsyncGraph <pyeitaa.raw.functions.stats.LoadAsyncGraph>`
    """

    QUALNAME = "pyeitaa.raw.base.StatsGraph"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
