from io import BytesIO

from pyeitaa.raw.core.primitives import Int, Long, String
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class Authorization(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.Authorization`.

    Details:
        - Layer: ``135``
        - ID: ``-0x52fe29e3``

    Parameters:
        hash: ``int`` ``64-bit``
        device_model: ``str``
        platform: ``str``
        system_version: ``str``
        api_id: ``int`` ``32-bit``
        app_name: ``str``
        app_version: ``str``
        date_created: ``int`` ``32-bit``
        date_active: ``int`` ``32-bit``
        ip: ``str``
        country: ``str``
        region: ``str``
        current (optional): ``bool``
        official_app (optional): ``bool``
        password_pending (optional): ``bool``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`auth.AcceptLoginToken <pyeitaa.raw.functions.auth.AcceptLoginToken>`
    """

    __slots__: List[str] = ["hash", "device_model", "platform", "system_version", "api_id", "app_name", "app_version", "date_created", "date_active", "ip", "country", "region", "current", "official_app", "password_pending"]

    ID = -0x52fe29e3
    QUALNAME = "types.Authorization"

    def __init__(self, *, hash: int, device_model: str, platform: str, system_version: str, api_id: int, app_name: str, app_version: str, date_created: int, date_active: int, ip: str, country: str, region: str, current: Optional[bool] = None, official_app: Optional[bool] = None, password_pending: Optional[bool] = None) -> None:
        self.hash = hash  # long
        self.device_model = device_model  # string
        self.platform = platform  # string
        self.system_version = system_version  # string
        self.api_id = api_id  # int
        self.app_name = app_name  # string
        self.app_version = app_version  # string
        self.date_created = date_created  # int
        self.date_active = date_active  # int
        self.ip = ip  # string
        self.country = country  # string
        self.region = region  # string
        self.current = current  # flags.0?true
        self.official_app = official_app  # flags.1?true
        self.password_pending = password_pending  # flags.2?true

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        current = True if flags & (1 << 0) else False
        official_app = True if flags & (1 << 1) else False
        password_pending = True if flags & (1 << 2) else False
        hash = Long.read(data)
        
        device_model = String.read(data)
        
        platform = String.read(data)
        
        system_version = String.read(data)
        
        api_id = Int.read(data)
        
        app_name = String.read(data)
        
        app_version = String.read(data)
        
        date_created = Int.read(data)
        
        date_active = Int.read(data)
        
        ip = String.read(data)
        
        country = String.read(data)
        
        region = String.read(data)
        
        return Authorization(hash=hash, device_model=device_model, platform=platform, system_version=system_version, api_id=api_id, app_name=app_name, app_version=app_version, date_created=date_created, date_active=date_active, ip=ip, country=country, region=region, current=current, official_app=official_app, password_pending=password_pending)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.current else 0
        flags |= (1 << 1) if self.official_app else 0
        flags |= (1 << 2) if self.password_pending else 0
        data.write(Int(flags))
        
        data.write(Long(self.hash))
        
        data.write(String(self.device_model))
        
        data.write(String(self.platform))
        
        data.write(String(self.system_version))
        
        data.write(Int(self.api_id))
        
        data.write(String(self.app_name))
        
        data.write(String(self.app_version))
        
        data.write(Int(self.date_created))
        
        data.write(Int(self.date_active))
        
        data.write(String(self.ip))
        
        data.write(String(self.country))
        
        data.write(String(self.region))
        
        return data.getvalue()
