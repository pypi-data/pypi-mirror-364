from typing import Union
from pyeitaa import raw

BroadcastStats = Union[raw.types.stats.BroadcastStats]


# noinspection PyRedeclaration
class BroadcastStats:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`stats.BroadcastStats <pyeitaa.raw.types.stats.BroadcastStats>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`stats.GetBroadcastStats <pyeitaa.raw.functions.stats.GetBroadcastStats>`
    """

    QUALNAME = "pyeitaa.raw.base.stats.BroadcastStats"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
