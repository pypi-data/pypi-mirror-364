from typing import Union
from pyeitaa import raw

ResPQ = Union[raw.types.ResPQ, raw.types.ResPQ]


# noinspection PyRedeclaration
class ResPQ:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ResPQ <pyeitaa.raw.types.ResPQ>`
            - :obj:`ResPQ <pyeitaa.raw.types.ResPQ>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`ReqPq <pyeitaa.raw.functions.ReqPq>`
            - :obj:`ReqPqMulti <pyeitaa.raw.functions.ReqPqMulti>`
            - :obj:`ReqPqMulti <pyeitaa.raw.functions.ReqPqMulti>`
    """

    QUALNAME = "pyeitaa.raw.base.ResPQ"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
