from typing import Union
from pyeitaa import raw

LiveStream = Union[raw.types.LiveStream]


# noinspection PyRedeclaration
class LiveStream:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`LiveStream <pyeitaa.raw.types.LiveStream>`
    """

    QUALNAME = "pyeitaa.raw.base.LiveStream"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
