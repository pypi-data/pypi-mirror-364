from typing import Union
from pyeitaa import raw

RpcDropAnswer = Union[raw.types.RpcAnswerDropped, raw.types.RpcAnswerDropped, raw.types.RpcAnswerDroppedRunning, raw.types.RpcAnswerDroppedRunning, raw.types.RpcAnswerUnknown, raw.types.RpcAnswerUnknown]


# noinspection PyRedeclaration
class RpcDropAnswer:
    """This base type has 6 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`RpcAnswerDropped <pyeitaa.raw.types.RpcAnswerDropped>`
            - :obj:`RpcAnswerDropped <pyeitaa.raw.types.RpcAnswerDropped>`
            - :obj:`RpcAnswerDroppedRunning <pyeitaa.raw.types.RpcAnswerDroppedRunning>`
            - :obj:`RpcAnswerDroppedRunning <pyeitaa.raw.types.RpcAnswerDroppedRunning>`
            - :obj:`RpcAnswerUnknown <pyeitaa.raw.types.RpcAnswerUnknown>`
            - :obj:`RpcAnswerUnknown <pyeitaa.raw.types.RpcAnswerUnknown>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`RpcDropAnswer <pyeitaa.raw.functions.RpcDropAnswer>`
            - :obj:`RpcDropAnswer <pyeitaa.raw.functions.RpcDropAnswer>`
    """

    QUALNAME = "pyeitaa.raw.base.RpcDropAnswer"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
