import os
import pathlib
from typing import Any, Coroutine
import aiohttp
from aiohttp import FormData
from aiohttp.abc import AbstractStreamWriter
from aiohttp.payload import Payload, PAYLOAD_REGISTRY, Order
from aiohttp.http_writer import StreamWriter


class SendFile:
    file_path: pathlib.Path
    def __init__(self, file_path: str):
        self.file_path = pathlib.Path(file_path)

    

class FilePayload(Payload):
    def __init__(self, sendfile:SendFile, *args, **kwargs):
        super().__init__(sendfile, *args, **kwargs)

    
    async def write(self, writer: StreamWriter) -> Coroutine[Any, Any, None]:
        if self._value:
            sendfile:SendFile = self._value
            with open(sendfile.file_path, 'rb') as fp:
                file_size = os.fstat(fp.fileno()).st_size
                chunk_len_pre = ("%x\r\n" % file_size).encode("ascii")
                writer._write(chunk_len_pre)
                for i in range(0, file_size, 0xffff_ffff>>1):
                    size = await writer.loop.sendfile(
                        writer.transport, fp, i, 0xffff_ffff>>1
                    )
                    writer.buffer_size += size
                    writer.output_size += size
                writer._write(b"\r\n")

PAYLOAD_REGISTRY.register(FilePayload, SendFile, order=Order.try_last)