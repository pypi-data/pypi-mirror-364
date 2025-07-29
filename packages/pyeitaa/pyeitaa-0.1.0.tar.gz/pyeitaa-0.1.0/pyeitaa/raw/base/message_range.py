from typing import Union
from pyeitaa import raw

MessageRange = Union[raw.types.MessageRange]


# noinspection PyRedeclaration
class MessageRange:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`MessageRange <pyeitaa.raw.types.MessageRange>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetSplitRanges <pyeitaa.raw.functions.messages.GetSplitRanges>`
    """

    QUALNAME = "pyeitaa.raw.base.MessageRange"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
