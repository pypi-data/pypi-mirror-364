from typing import Union
from pyeitaa import raw

CountriesList = Union[raw.types.help.CountriesList, raw.types.help.CountriesListNotModified]


# noinspection PyRedeclaration
class CountriesList:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`help.CountriesList <pyeitaa.raw.types.help.CountriesList>`
            - :obj:`help.CountriesListNotModified <pyeitaa.raw.types.help.CountriesListNotModified>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetCountriesList <pyeitaa.raw.functions.help.GetCountriesList>`
    """

    QUALNAME = "pyeitaa.raw.base.help.CountriesList"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
