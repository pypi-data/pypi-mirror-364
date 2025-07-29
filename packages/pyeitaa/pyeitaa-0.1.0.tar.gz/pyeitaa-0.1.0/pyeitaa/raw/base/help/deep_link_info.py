from typing import Union
from pyeitaa import raw

DeepLinkInfo = Union[raw.types.help.DeepLinkInfo, raw.types.help.DeepLinkInfoEmpty]


# noinspection PyRedeclaration
class DeepLinkInfo:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`help.DeepLinkInfo <pyeitaa.raw.types.help.DeepLinkInfo>`
            - :obj:`help.DeepLinkInfoEmpty <pyeitaa.raw.types.help.DeepLinkInfoEmpty>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetDeepLinkInfo <pyeitaa.raw.functions.help.GetDeepLinkInfo>`
    """

    QUALNAME = "pyeitaa.raw.base.help.DeepLinkInfo"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
