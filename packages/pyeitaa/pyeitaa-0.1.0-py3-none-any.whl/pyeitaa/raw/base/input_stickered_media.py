from typing import Union
from pyeitaa import raw

InputStickeredMedia = Union[raw.types.InputStickeredMediaDocument, raw.types.InputStickeredMediaPhoto]


# noinspection PyRedeclaration
class InputStickeredMedia:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputStickeredMediaDocument <pyeitaa.raw.types.InputStickeredMediaDocument>`
            - :obj:`InputStickeredMediaPhoto <pyeitaa.raw.types.InputStickeredMediaPhoto>`
    """

    QUALNAME = "pyeitaa.raw.base.InputStickeredMedia"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
