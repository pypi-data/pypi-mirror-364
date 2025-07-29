from typing import Union
from pyeitaa import raw

StickerSetInstallResult = Union[raw.types.messages.StickerSetInstallResultArchive, raw.types.messages.StickerSetInstallResultSuccess]


# noinspection PyRedeclaration
class StickerSetInstallResult:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.StickerSetInstallResultArchive <pyeitaa.raw.types.messages.StickerSetInstallResultArchive>`
            - :obj:`messages.StickerSetInstallResultSuccess <pyeitaa.raw.types.messages.StickerSetInstallResultSuccess>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.InstallStickerSet <pyeitaa.raw.functions.messages.InstallStickerSet>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.StickerSetInstallResult"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
