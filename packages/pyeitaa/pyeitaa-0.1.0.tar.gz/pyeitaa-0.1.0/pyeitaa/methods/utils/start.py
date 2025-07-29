import logging

import pyeitaa
from ...raw.functions.help.get_config import GetConfig
from ...raw.functions.updates.get_state import GetState
from ...session_internals import DataCenter, KNOWN_DATACENTERS
from ...errors.exceptions import RPCError


log = logging.getLogger(__name__)


class Start:
    async def start(self: "pyeitaa.Client"):
        if self.is_initialized:
            return
                
        await self.load_session()

        config = await self.invoke(
            GetConfig(), check_connection=False
        )

        data_centers = {
            f"https://{dc.ip_address}/eitaa/"
            for dc in config.dc_options
            if not dc.ipv6
            if dc.port == 443
        }

        DataCenter.CLIENT_DATACENTERS.extend(data_centers & KNOWN_DATACENTERS.CLIENT_DATACENTERS)
        DataCenter.UPLOAD_DATACENTERS.extend(data_centers & KNOWN_DATACENTERS.UPLOAD_DATACENTERS)
        DataCenter.DOWNLOAD_DATACENTERS.extend(data_centers & KNOWN_DATACENTERS.DOWNLOAD_DATACENTERS)

        try:
            await self.invoke(GetState(), check_connection=False)
            self.me = await self.get_me(check_connection=False)

        except RPCError:            
            self.me = await self.authorize()

        self.is_initialized = True

        return self
