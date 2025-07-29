from typing import Union
from pyeitaa import raw

LangPackDifference = Union[raw.types.LangPackDifference]


# noinspection PyRedeclaration
class LangPackDifference:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`LangPackDifference <pyeitaa.raw.types.LangPackDifference>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`langpack.GetLangPack <pyeitaa.raw.functions.langpack.GetLangPack>`
            - :obj:`langpack.GetDifference <pyeitaa.raw.functions.langpack.GetDifference>`
    """

    QUALNAME = "pyeitaa.raw.base.LangPackDifference"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
