from typing import Union
from pyeitaa import raw

MegagroupStats = Union[raw.types.stats.MegagroupStats]


# noinspection PyRedeclaration
class MegagroupStats:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`stats.MegagroupStats <pyeitaa.raw.types.stats.MegagroupStats>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`stats.GetMegagroupStats <pyeitaa.raw.functions.stats.GetMegagroupStats>`
    """

    QUALNAME = "pyeitaa.raw.base.stats.MegagroupStats"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
