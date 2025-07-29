from typing import Union
from pyeitaa import raw

TermsOfService = Union[raw.types.help.TermsOfService]


# noinspection PyRedeclaration
class TermsOfService:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`help.TermsOfService <pyeitaa.raw.types.help.TermsOfService>`
    """

    QUALNAME = "pyeitaa.raw.base.help.TermsOfService"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
