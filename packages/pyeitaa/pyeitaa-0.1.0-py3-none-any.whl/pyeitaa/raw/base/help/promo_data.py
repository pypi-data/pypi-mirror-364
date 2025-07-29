from typing import Union
from pyeitaa import raw

PromoData = Union[raw.types.help.PromoData, raw.types.help.PromoDataEmpty]


# noinspection PyRedeclaration
class PromoData:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`help.PromoData <pyeitaa.raw.types.help.PromoData>`
            - :obj:`help.PromoDataEmpty <pyeitaa.raw.types.help.PromoDataEmpty>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetPromoData <pyeitaa.raw.functions.help.GetPromoData>`
    """

    QUALNAME = "pyeitaa.raw.base.help.PromoData"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
