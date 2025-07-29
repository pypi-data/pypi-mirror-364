from typing import Union
from pyeitaa import raw

SponsoredMessages = Union[raw.types.messages.SponsoredMessages]


# noinspection PyRedeclaration
class SponsoredMessages:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.SponsoredMessages <pyeitaa.raw.types.messages.SponsoredMessages>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`channels.GetSponsoredMessages <pyeitaa.raw.functions.channels.GetSponsoredMessages>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.SponsoredMessages"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
