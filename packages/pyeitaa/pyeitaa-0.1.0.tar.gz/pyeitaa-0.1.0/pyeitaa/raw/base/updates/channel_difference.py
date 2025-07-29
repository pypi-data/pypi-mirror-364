from typing import Union
from pyeitaa import raw

ChannelDifference = Union[raw.types.updates.ChannelDifference, raw.types.updates.ChannelDifferenceEmpty, raw.types.updates.ChannelDifferenceTooLong]


# noinspection PyRedeclaration
class ChannelDifference:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`updates.ChannelDifference <pyeitaa.raw.types.updates.ChannelDifference>`
            - :obj:`updates.ChannelDifferenceEmpty <pyeitaa.raw.types.updates.ChannelDifferenceEmpty>`
            - :obj:`updates.ChannelDifferenceTooLong <pyeitaa.raw.types.updates.ChannelDifferenceTooLong>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`updates.GetChannelDifference <pyeitaa.raw.functions.updates.GetChannelDifference>`
    """

    QUALNAME = "pyeitaa.raw.base.updates.ChannelDifference"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
