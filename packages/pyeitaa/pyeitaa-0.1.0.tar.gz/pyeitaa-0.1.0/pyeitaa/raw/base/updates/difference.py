from typing import Union
from pyeitaa import raw

Difference = Union[raw.types.updates.Difference, raw.types.updates.DifferenceEmpty, raw.types.updates.DifferenceSlice, raw.types.updates.DifferenceTooLong]


# noinspection PyRedeclaration
class Difference:
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`updates.Difference <pyeitaa.raw.types.updates.Difference>`
            - :obj:`updates.DifferenceEmpty <pyeitaa.raw.types.updates.DifferenceEmpty>`
            - :obj:`updates.DifferenceSlice <pyeitaa.raw.types.updates.DifferenceSlice>`
            - :obj:`updates.DifferenceTooLong <pyeitaa.raw.types.updates.DifferenceTooLong>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`updates.GetDifference <pyeitaa.raw.functions.updates.GetDifference>`
    """

    QUALNAME = "pyeitaa.raw.base.updates.Difference"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
