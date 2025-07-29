from typing import Union
from pyeitaa import raw

HistoryImport = Union[raw.types.messages.HistoryImport]


# noinspection PyRedeclaration
class HistoryImport:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.HistoryImport <pyeitaa.raw.types.messages.HistoryImport>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.InitHistoryImport <pyeitaa.raw.functions.messages.InitHistoryImport>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.HistoryImport"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
