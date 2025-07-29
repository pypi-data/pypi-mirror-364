from typing import Union
from pyeitaa import raw

SetClientDHParamsAnswer = Union[raw.types.DhGenFail, raw.types.DhGenFail, raw.types.DhGenOk, raw.types.DhGenOk, raw.types.DhGenRetry, raw.types.DhGenRetry]


# noinspection PyRedeclaration
class SetClientDHParamsAnswer:
    """This base type has 6 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`DhGenFail <pyeitaa.raw.types.DhGenFail>`
            - :obj:`DhGenFail <pyeitaa.raw.types.DhGenFail>`
            - :obj:`DhGenOk <pyeitaa.raw.types.DhGenOk>`
            - :obj:`DhGenOk <pyeitaa.raw.types.DhGenOk>`
            - :obj:`DhGenRetry <pyeitaa.raw.types.DhGenRetry>`
            - :obj:`DhGenRetry <pyeitaa.raw.types.DhGenRetry>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`SetClientDHParams <pyeitaa.raw.functions.SetClientDHParams>`
            - :obj:`SetClientDHParams <pyeitaa.raw.functions.SetClientDHParams>`
    """

    QUALNAME = "pyeitaa.raw.base.SetClientDHParamsAnswer"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
