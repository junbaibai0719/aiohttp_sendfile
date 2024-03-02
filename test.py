
import asyncio
import pathlib
import aiohttp

import aiofiles

from aiohttp_sendfile import SendFile


async def file_sender(file_path):
    async with aiofiles.open(file_path, 'rb') as f:
        while chunk := await f.read(1024*1024*8):
            yield chunk

async def upload(sess:aiohttp.ClientSession, file_path:pathlib.Path):
    data = aiohttp.FormData(quote_fields=False)
    data.add_field('file', file_sender(file_path), filename=file_path.name)
    async with sess.post('http://localhost:8080/upload', data=data) as resp:
        print(resp.request_info)
        print(await resp.text())

async def upload_sendfile(sess:aiohttp.ClientSession, file_path:pathlib.Path):
    data = aiohttp.FormData(quote_fields=False)
    data.add_field('file', SendFile(file_path), filename="sendfile"+file_path.name)
    async with sess.post('http://localhost:8080/upload', data=data) as resp:
        print(resp.request_info)
        print(await resp.text())

async def main():
    async with aiohttp.ClientSession() as sess:
        await upload(sess, pathlib.Path('test.py'))
        await upload_sendfile(sess, pathlib.Path('test.py'))
        with open("./uploads/sendfiletest.py", "rb") as fp, open("./uploads/test.py", "rb") as fp2:
            assert fp.read() == fp2.read()

asyncio.run(main())