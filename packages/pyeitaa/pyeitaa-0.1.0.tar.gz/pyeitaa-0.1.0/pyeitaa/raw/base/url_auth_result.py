from typing import Union
from pyeitaa import raw

UrlAuthResult = Union[raw.types.UrlAuthResultAccepted, raw.types.UrlAuthResultDefault, raw.types.UrlAuthResultRequest]


# noinspection PyRedeclaration
class UrlAuthResult:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`UrlAuthResultAccepted <pyeitaa.raw.types.UrlAuthResultAccepted>`
            - :obj:`UrlAuthResultDefault <pyeitaa.raw.types.UrlAuthResultDefault>`
            - :obj:`UrlAuthResultRequest <pyeitaa.raw.types.UrlAuthResultRequest>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.RequestUrlAuth <pyeitaa.raw.functions.messages.RequestUrlAuth>`
            - :obj:`messages.AcceptUrlAuth <pyeitaa.raw.functions.messages.AcceptUrlAuth>`
    """

    QUALNAME = "pyeitaa.raw.base.UrlAuthResult"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
