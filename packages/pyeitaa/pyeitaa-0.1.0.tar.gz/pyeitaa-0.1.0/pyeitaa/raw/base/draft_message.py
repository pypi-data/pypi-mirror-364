from typing import Union
from pyeitaa import raw

DraftMessage = Union[raw.types.DraftMessage, raw.types.DraftMessageEmpty]


# noinspection PyRedeclaration
class DraftMessage:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`DraftMessage <pyeitaa.raw.types.DraftMessage>`
            - :obj:`DraftMessageEmpty <pyeitaa.raw.types.DraftMessageEmpty>`
    """

    QUALNAME = "pyeitaa.raw.base.DraftMessage"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
