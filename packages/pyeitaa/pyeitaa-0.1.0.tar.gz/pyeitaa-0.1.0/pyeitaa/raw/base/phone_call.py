from typing import Union
from pyeitaa import raw

PhoneCall = Union[raw.types.PhoneCall, raw.types.PhoneCallAccepted, raw.types.PhoneCallDiscarded, raw.types.PhoneCallEmpty, raw.types.PhoneCallRequested, raw.types.PhoneCallWaiting]


# noinspection PyRedeclaration
class PhoneCall:
    """This base type has 6 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PhoneCall <pyeitaa.raw.types.PhoneCall>`
            - :obj:`PhoneCallAccepted <pyeitaa.raw.types.PhoneCallAccepted>`
            - :obj:`PhoneCallDiscarded <pyeitaa.raw.types.PhoneCallDiscarded>`
            - :obj:`PhoneCallEmpty <pyeitaa.raw.types.PhoneCallEmpty>`
            - :obj:`PhoneCallRequested <pyeitaa.raw.types.PhoneCallRequested>`
            - :obj:`PhoneCallWaiting <pyeitaa.raw.types.PhoneCallWaiting>`
    """

    QUALNAME = "pyeitaa.raw.base.PhoneCall"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
