from typing import Union
from pyeitaa import raw

AdsClickAction = Union[raw.types.AdsIntentAction, raw.types.AdsOpenExternalLinkAction, raw.types.AdsOpenLinkAction]


# noinspection PyRedeclaration
class AdsClickAction:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`AdsIntentAction <pyeitaa.raw.types.AdsIntentAction>`
            - :obj:`AdsOpenExternalLinkAction <pyeitaa.raw.types.AdsOpenExternalLinkAction>`
            - :obj:`AdsOpenLinkAction <pyeitaa.raw.types.AdsOpenLinkAction>`
    """

    QUALNAME = "pyeitaa.raw.base.AdsClickAction"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
