from typing import Union
from pyeitaa import raw

LangPackLanguage = Union[raw.types.LangPackLanguage]


# noinspection PyRedeclaration
class LangPackLanguage:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`LangPackLanguage <pyeitaa.raw.types.LangPackLanguage>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`langpack.GetLanguages <pyeitaa.raw.functions.langpack.GetLanguages>`
            - :obj:`langpack.GetLanguage <pyeitaa.raw.functions.langpack.GetLanguage>`
    """

    QUALNAME = "pyeitaa.raw.base.LangPackLanguage"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
