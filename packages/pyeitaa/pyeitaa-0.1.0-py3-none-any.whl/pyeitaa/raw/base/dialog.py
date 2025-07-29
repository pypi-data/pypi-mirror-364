from typing import Union
from pyeitaa import raw

Dialog = Union[raw.types.Dialog, raw.types.DialogFolder]


# noinspection PyRedeclaration
class Dialog:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`Dialog <pyeitaa.raw.types.Dialog>`
            - :obj:`DialogFolder <pyeitaa.raw.types.DialogFolder>`
    """

    QUALNAME = "pyeitaa.raw.base.Dialog"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
