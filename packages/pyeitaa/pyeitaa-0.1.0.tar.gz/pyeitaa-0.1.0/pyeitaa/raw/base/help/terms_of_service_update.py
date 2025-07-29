from typing import Union
from pyeitaa import raw

TermsOfServiceUpdate = Union[raw.types.help.TermsOfServiceUpdate, raw.types.help.TermsOfServiceUpdateEmpty]


# noinspection PyRedeclaration
class TermsOfServiceUpdate:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`help.TermsOfServiceUpdate <pyeitaa.raw.types.help.TermsOfServiceUpdate>`
            - :obj:`help.TermsOfServiceUpdateEmpty <pyeitaa.raw.types.help.TermsOfServiceUpdateEmpty>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetTermsOfServiceUpdate <pyeitaa.raw.functions.help.GetTermsOfServiceUpdate>`
    """

    QUALNAME = "pyeitaa.raw.base.help.TermsOfServiceUpdate"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
