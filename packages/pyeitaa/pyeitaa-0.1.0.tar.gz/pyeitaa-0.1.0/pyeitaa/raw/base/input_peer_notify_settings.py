from typing import Union
from pyeitaa import raw

InputPeerNotifySettings = Union[raw.types.InputPeerNotifySettings]


# noinspection PyRedeclaration
class InputPeerNotifySettings:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputPeerNotifySettings <pyeitaa.raw.types.InputPeerNotifySettings>`
    """

    QUALNAME = "pyeitaa.raw.base.InputPeerNotifySettings"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
