from typing import Union
from pyeitaa import raw

InlineBotSwitchPM = Union[raw.types.InlineBotSwitchPM]


# noinspection PyRedeclaration
class InlineBotSwitchPM:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InlineBotSwitchPM <pyeitaa.raw.types.InlineBotSwitchPM>`
    """

    QUALNAME = "pyeitaa.raw.base.InlineBotSwitchPM"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
