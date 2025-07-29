from typing import Union
from pyeitaa import raw

HistoryImportParsed = Union[raw.types.messages.HistoryImportParsed]


# noinspection PyRedeclaration
class HistoryImportParsed:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.HistoryImportParsed <pyeitaa.raw.types.messages.HistoryImportParsed>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.CheckHistoryImport <pyeitaa.raw.functions.messages.CheckHistoryImport>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.HistoryImportParsed"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
