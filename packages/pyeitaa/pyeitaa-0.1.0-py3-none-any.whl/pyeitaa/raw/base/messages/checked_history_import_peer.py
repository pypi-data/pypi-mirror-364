from typing import Union
from pyeitaa import raw

CheckedHistoryImportPeer = Union[raw.types.messages.CheckedHistoryImportPeer]


# noinspection PyRedeclaration
class CheckedHistoryImportPeer:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.CheckedHistoryImportPeer <pyeitaa.raw.types.messages.CheckedHistoryImportPeer>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.CheckHistoryImportPeer <pyeitaa.raw.functions.messages.CheckHistoryImportPeer>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.CheckedHistoryImportPeer"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
