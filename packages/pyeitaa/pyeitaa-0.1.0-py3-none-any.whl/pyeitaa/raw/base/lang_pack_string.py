from typing import Union
from pyeitaa import raw

LangPackString = Union[raw.types.LangPackString, raw.types.LangPackStringDeleted, raw.types.LangPackStringPluralized]


# noinspection PyRedeclaration
class LangPackString:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`LangPackString <pyeitaa.raw.types.LangPackString>`
            - :obj:`LangPackStringDeleted <pyeitaa.raw.types.LangPackStringDeleted>`
            - :obj:`LangPackStringPluralized <pyeitaa.raw.types.LangPackStringPluralized>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`langpack.GetStrings <pyeitaa.raw.functions.langpack.GetStrings>`
    """

    QUALNAME = "pyeitaa.raw.base.LangPackString"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
