from typing import Union
from pyeitaa import raw

AffectedFoundMessages = Union[raw.types.messages.AffectedFoundMessages]


# noinspection PyRedeclaration
class AffectedFoundMessages:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.AffectedFoundMessages <pyeitaa.raw.types.messages.AffectedFoundMessages>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.DeletePhoneCallHistory <pyeitaa.raw.functions.messages.DeletePhoneCallHistory>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.AffectedFoundMessages"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
