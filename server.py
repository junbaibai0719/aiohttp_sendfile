import pathlib
from aiohttp import BodyPartReader, MultipartReader
from aiohttp.web import Application, Response, Request
from aiohttp import web
import aiofiles

upload_folder = "./uploads/"


async def upload(request: Request) -> Response:
    parts = await request.multipart()
    file:BodyPartReader = None
    while field := await parts.next():
        if field.name == "file":
            file = field
            break
    else:
        return web.json_response({"error": "No file part in the request"})
    if file:
        save_path = pathlib.Path(upload_folder).joinpath(file.filename.strip())
        save_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(save_path, "wb") as f:
            while chunk := await file.read_chunk():
                await f.write(chunk)
        return Response(text=f"文件 {file.filename} 上传成功！")
    else:
        return Response(text="文件上传失败！", status=400)


app = Application()
app.add_routes([web.post("/upload", upload)])
web.run_app(app)