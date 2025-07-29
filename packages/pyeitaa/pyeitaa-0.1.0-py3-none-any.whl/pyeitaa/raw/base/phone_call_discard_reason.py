from typing import Union
from pyeitaa import raw

PhoneCallDiscardReason = Union[raw.types.PhoneCallDiscardReasonBusy, raw.types.PhoneCallDiscardReasonDisconnect, raw.types.PhoneCallDiscardReasonHangup, raw.types.PhoneCallDiscardReasonMissed]


# noinspection PyRedeclaration
class PhoneCallDiscardReason:
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PhoneCallDiscardReasonBusy <pyeitaa.raw.types.PhoneCallDiscardReasonBusy>`
            - :obj:`PhoneCallDiscardReasonDisconnect <pyeitaa.raw.types.PhoneCallDiscardReasonDisconnect>`
            - :obj:`PhoneCallDiscardReasonHangup <pyeitaa.raw.types.PhoneCallDiscardReasonHangup>`
            - :obj:`PhoneCallDiscardReasonMissed <pyeitaa.raw.types.PhoneCallDiscardReasonMissed>`
    """

    QUALNAME = "pyeitaa.raw.base.PhoneCallDiscardReason"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
