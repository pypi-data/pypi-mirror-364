from typing import Union
from pyeitaa import raw

PhoneCall = Union[raw.types.phone.PhoneCall]


# noinspection PyRedeclaration
class PhoneCall:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`phone.PhoneCall <pyeitaa.raw.types.phone.PhoneCall>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`phone.RequestCall <pyeitaa.raw.functions.phone.RequestCall>`
            - :obj:`phone.AcceptCall <pyeitaa.raw.functions.phone.AcceptCall>`
            - :obj:`phone.ConfirmCall <pyeitaa.raw.functions.phone.ConfirmCall>`
    """

    QUALNAME = "pyeitaa.raw.base.phone.PhoneCall"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
