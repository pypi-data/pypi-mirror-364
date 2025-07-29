from typing import Union
from pyeitaa import raw

ExportedMessageLink = Union[raw.types.ExportedMessageLink]


# noinspection PyRedeclaration
class ExportedMessageLink:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ExportedMessageLink <pyeitaa.raw.types.ExportedMessageLink>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`channels.ExportMessageLink <pyeitaa.raw.functions.channels.ExportMessageLink>`
    """

    QUALNAME = "pyeitaa.raw.base.ExportedMessageLink"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
