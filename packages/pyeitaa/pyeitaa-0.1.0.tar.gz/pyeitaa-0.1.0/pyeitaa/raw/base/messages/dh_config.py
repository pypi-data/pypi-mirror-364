from typing import Union
from pyeitaa import raw

DhConfig = Union[raw.types.messages.DhConfig, raw.types.messages.DhConfigNotModified]


# noinspection PyRedeclaration
class DhConfig:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.DhConfig <pyeitaa.raw.types.messages.DhConfig>`
            - :obj:`messages.DhConfigNotModified <pyeitaa.raw.types.messages.DhConfigNotModified>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetDhConfig <pyeitaa.raw.functions.messages.GetDhConfig>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.DhConfig"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
