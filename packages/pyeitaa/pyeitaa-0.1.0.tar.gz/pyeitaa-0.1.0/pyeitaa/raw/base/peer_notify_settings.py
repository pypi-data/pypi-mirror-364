from typing import Union
from pyeitaa import raw

PeerNotifySettings = Union[raw.types.PeerNotifySettings]


# noinspection PyRedeclaration
class PeerNotifySettings:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PeerNotifySettings <pyeitaa.raw.types.PeerNotifySettings>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetNotifySettings <pyeitaa.raw.functions.account.GetNotifySettings>`
    """

    QUALNAME = "pyeitaa.raw.base.PeerNotifySettings"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
