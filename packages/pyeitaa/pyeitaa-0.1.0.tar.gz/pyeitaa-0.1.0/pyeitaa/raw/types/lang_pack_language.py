from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class LangPackLanguage(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.LangPackLanguage`.

    Details:
        - Layer: ``135``
        - ID: ``-0x1135a31d``

    Parameters:
        name: ``str``
        native_name: ``str``
        lang_code: ``str``
        plural_code: ``str``
        strings_count: ``int`` ``32-bit``
        translated_count: ``int`` ``32-bit``
        translations_url: ``str``
        official (optional): ``bool``
        rtl (optional): ``bool``
        beta (optional): ``bool``
        base_lang_code (optional): ``str``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`langpack.GetLanguages <pyeitaa.raw.functions.langpack.GetLanguages>`
            - :obj:`langpack.GetLanguage <pyeitaa.raw.functions.langpack.GetLanguage>`
    """

    __slots__: List[str] = ["name", "native_name", "lang_code", "plural_code", "strings_count", "translated_count", "translations_url", "official", "rtl", "beta", "base_lang_code"]

    ID = -0x1135a31d
    QUALNAME = "types.LangPackLanguage"

    def __init__(self, *, name: str, native_name: str, lang_code: str, plural_code: str, strings_count: int, translated_count: int, translations_url: str, official: Optional[bool] = None, rtl: Optional[bool] = None, beta: Optional[bool] = None, base_lang_code: Optional[str] = None) -> None:
        self.name = name  # string
        self.native_name = native_name  # string
        self.lang_code = lang_code  # string
        self.plural_code = plural_code  # string
        self.strings_count = strings_count  # int
        self.translated_count = translated_count  # int
        self.translations_url = translations_url  # string
        self.official = official  # flags.0?true
        self.rtl = rtl  # flags.2?true
        self.beta = beta  # flags.3?true
        self.base_lang_code = base_lang_code  # flags.1?string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        official = True if flags & (1 << 0) else False
        rtl = True if flags & (1 << 2) else False
        beta = True if flags & (1 << 3) else False
        name = String.read(data)
        
        native_name = String.read(data)
        
        lang_code = String.read(data)
        
        base_lang_code = String.read(data) if flags & (1 << 1) else None
        plural_code = String.read(data)
        
        strings_count = Int.read(data)
        
        translated_count = Int.read(data)
        
        translations_url = String.read(data)
        
        return LangPackLanguage(name=name, native_name=native_name, lang_code=lang_code, plural_code=plural_code, strings_count=strings_count, translated_count=translated_count, translations_url=translations_url, official=official, rtl=rtl, beta=beta, base_lang_code=base_lang_code)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.official else 0
        flags |= (1 << 2) if self.rtl else 0
        flags |= (1 << 3) if self.beta else 0
        flags |= (1 << 1) if self.base_lang_code is not None else 0
        data.write(Int(flags))
        
        data.write(String(self.name))
        
        data.write(String(self.native_name))
        
        data.write(String(self.lang_code))
        
        if self.base_lang_code is not None:
            data.write(String(self.base_lang_code))
        
        data.write(String(self.plural_code))
        
        data.write(Int(self.strings_count))
        
        data.write(Int(self.translated_count))
        
        data.write(String(self.translations_url))
        
        return data.getvalue()
