from typing import Union
from pyeitaa import raw

InputContact = Union[raw.types.InputPhoneContact]


# noinspection PyRedeclaration
class InputContact:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputPhoneContact <pyeitaa.raw.types.InputPhoneContact>`
    """

    QUALNAME = "pyeitaa.raw.base.InputContact"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
