from typing import Union
from pyeitaa import raw

SavedInfo = Union[raw.types.payments.SavedInfo]


# noinspection PyRedeclaration
class SavedInfo:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`payments.SavedInfo <pyeitaa.raw.types.payments.SavedInfo>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`payments.GetSavedInfo <pyeitaa.raw.functions.payments.GetSavedInfo>`
    """

    QUALNAME = "pyeitaa.raw.base.payments.SavedInfo"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
