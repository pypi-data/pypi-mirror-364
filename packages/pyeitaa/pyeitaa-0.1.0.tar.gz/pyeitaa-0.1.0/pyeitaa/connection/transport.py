from io import BytesIO
from aiohttp import ClientSession, ClientTimeout

import logging

from ..session_internals import DataCenter, DcType

log = logging.getLogger(__name__)


class Transporter(ClientSession):
    def __init__(self, custom_header: str = None):
        super().__init__(timeout=ClientTimeout(10))
        self.headers["user-agent"] = custom_header or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"

    async def close(self):
        await super().close()

        log.info("Disconnected")

    async def send(self, data: bytes, dc_type: DcType = DcType.CLIENT) -> BytesIO:
        try:
            async with self.post(dc := DataCenter(dc_type), data=data) as response:
                if response.ok:
                    return BytesIO(
                        await response.content.read()
                    )

                DataCenter.mark_dc_as_failed(dc_type, dc)
                log.info("%s failed to connect in %s type", dc, dc_type)

                return await self.send(data, dc_type)

        except:
            DataCenter.mark_dc_as_failed(dc_type, dc)
            log.info("%s failed to connect in %s type", dc, dc_type)

            return await self.send(data, dc_type)