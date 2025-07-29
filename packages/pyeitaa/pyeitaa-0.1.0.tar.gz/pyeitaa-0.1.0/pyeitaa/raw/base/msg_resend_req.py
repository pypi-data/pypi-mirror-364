from typing import Union
from pyeitaa import raw

MsgResendReq = Union[raw.types.MsgResendAnsReq, raw.types.MsgResendReq, raw.types.MsgResendReq]


# noinspection PyRedeclaration
class MsgResendReq:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`MsgResendAnsReq <pyeitaa.raw.types.MsgResendAnsReq>`
            - :obj:`MsgResendReq <pyeitaa.raw.types.MsgResendReq>`
            - :obj:`MsgResendReq <pyeitaa.raw.types.MsgResendReq>`
    """

    QUALNAME = "pyeitaa.raw.base.MsgResendReq"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
