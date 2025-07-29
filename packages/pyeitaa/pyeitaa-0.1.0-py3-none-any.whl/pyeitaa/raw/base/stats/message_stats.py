from typing import Union
from pyeitaa import raw

MessageStats = Union[raw.types.stats.MessageStats]


# noinspection PyRedeclaration
class MessageStats:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`stats.MessageStats <pyeitaa.raw.types.stats.MessageStats>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`stats.GetMessageStats <pyeitaa.raw.functions.stats.GetMessageStats>`
    """

    QUALNAME = "pyeitaa.raw.base.stats.MessageStats"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
