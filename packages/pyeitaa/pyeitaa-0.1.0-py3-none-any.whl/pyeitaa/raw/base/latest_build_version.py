from typing import Union
from pyeitaa import raw

LatestBuildVersion = Union[raw.types.LatestBuildVersion]


# noinspection PyRedeclaration
class LatestBuildVersion:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`LatestBuildVersion <pyeitaa.raw.types.LatestBuildVersion>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`GetLatestBuildVersion <pyeitaa.raw.functions.GetLatestBuildVersion>`
    """

    QUALNAME = "pyeitaa.raw.base.LatestBuildVersion"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
