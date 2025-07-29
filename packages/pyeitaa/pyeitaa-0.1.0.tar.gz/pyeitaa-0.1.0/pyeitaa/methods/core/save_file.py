import logging
from math import ceil
from io import BytesIO
from os import SEEK_END
from hashlib import md5

import pyeitaa
from ...raw.types.input_file import InputFile
from ...raw.types.input_file_big import InputFileBig
from ...raw.functions.upload.save_file_part import SaveFilePart
from ...raw.functions.upload.save_big_file_part import SaveBigFilePart

from ...session_internals import DcType

log = logging.getLogger(__name__)



class SaveFile:
    async def save_file(
        self: "pyeitaa.Client",
        file: BytesIO,
        file_name: str
    ):
        if file is None:
            return

        file_part = 0
        part_size = 262144 # 256Kb

        file.seek(0, SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size == 0:
            raise ValueError("File size equals to 0 B")

        if file_size > 67108864: # 64Mb
            part_size = 524288 # 512Kb
        
        elif file_size < 102400:  # 100Kb
            part_size = 32768  # 32Kb

        file_total_parts = ceil(file_size / part_size)

        if file_total_parts > 4000 or file_size >= 104857600: # 100Mb
            raise ValueError("File is too big")

        is_big = file_size >= 10485760 # 10Mb

        if not is_big:
            md5_sum = md5()

        file_id = self.rnd_id()

        functions = []

        with file:
            file.seek(part_size * file_part)

            while True:
                chunk = file.read(part_size)

                if not chunk:
                    if not is_big:
                        md5_sum = "".join(
                            format(i, "x").zfill(2) for i in md5_sum.digest()
                        )

                    break

                if is_big:
                    functions.append(
                        SaveBigFilePart(
                            file_id=file_id,
                            file_part=file_part,
                            file_total_parts=file_total_parts,
                            bytes=chunk
                        )
                    )

                else:
                    functions.append(
                        SaveFilePart(
                            file_id=file_id,
                            file_part=file_part,
                            bytes=chunk
                        )
                    )

                if not is_big:
                    md5_sum.update(chunk)

                file_part += 1

            for f in functions:
                await self.invoke(f, dc_type=DcType.UPLOAD)

            if is_big:
                return InputFileBig(
                    id=file_id,
                    parts=file_total_parts,
                    name=file_name
                )
            else:
                return InputFile(
                    id=file_id,
                    parts=file_total_parts,
                    name=file_name,
                    md5_checksum=md5_sum
                )