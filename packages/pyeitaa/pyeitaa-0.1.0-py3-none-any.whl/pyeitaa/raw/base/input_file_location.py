from typing import Union
from pyeitaa import raw

InputFileLocation = Union[raw.types.InputDocumentFileLocation, raw.types.InputEncryptedFileLocation, raw.types.InputFileLocation, raw.types.InputGroupCallStream, raw.types.InputPeerPhotoFileLocation, raw.types.InputPhotoFileLocation, raw.types.InputPhotoLegacyFileLocation, raw.types.InputSecureFileLocation, raw.types.InputStickerSetThumb, raw.types.InputTakeoutFileLocation]


# noinspection PyRedeclaration
class InputFileLocation:
    """This base type has 10 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputDocumentFileLocation <pyeitaa.raw.types.InputDocumentFileLocation>`
            - :obj:`InputEncryptedFileLocation <pyeitaa.raw.types.InputEncryptedFileLocation>`
            - :obj:`InputFileLocation <pyeitaa.raw.types.InputFileLocation>`
            - :obj:`InputGroupCallStream <pyeitaa.raw.types.InputGroupCallStream>`
            - :obj:`InputPeerPhotoFileLocation <pyeitaa.raw.types.InputPeerPhotoFileLocation>`
            - :obj:`InputPhotoFileLocation <pyeitaa.raw.types.InputPhotoFileLocation>`
            - :obj:`InputPhotoLegacyFileLocation <pyeitaa.raw.types.InputPhotoLegacyFileLocation>`
            - :obj:`InputSecureFileLocation <pyeitaa.raw.types.InputSecureFileLocation>`
            - :obj:`InputStickerSetThumb <pyeitaa.raw.types.InputStickerSetThumb>`
            - :obj:`InputTakeoutFileLocation <pyeitaa.raw.types.InputTakeoutFileLocation>`
    """

    QUALNAME = "pyeitaa.raw.base.InputFileLocation"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
