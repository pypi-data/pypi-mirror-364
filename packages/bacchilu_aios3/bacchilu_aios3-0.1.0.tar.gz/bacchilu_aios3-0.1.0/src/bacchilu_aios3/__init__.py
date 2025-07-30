from contextlib import asynccontextmanager
from typing import IO

import aioboto3
import magic


def guess_content_type(file_obj: IO[bytes]):
    current_pos = file_obj.tell()
    chunk = file_obj.read(4096)
    file_obj.seek(current_pos)
    mime_type = magic.from_buffer(chunk, mime=True)
    return mime_type or "application/octet-stream"


class Bucket:
    def __init__(self, bucket):
        self.bucket = bucket

    @classmethod
    @asynccontextmanager
    async def create_obj(
        cls,
        name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str,
    ):
        session = aioboto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )
        async with session.resource("s3") as s3:
            bucket = await s3.Bucket(name)
            yield cls(bucket)

    async def upload_fileobj(self, fp: IO[bytes], key: str):
        await self.bucket.upload_fileobj(
            fp, key, {"ACL": "public-read", "ContentType": guess_content_type(fp)}
        )

    async def download_fileobj(self, fp: IO[bytes], key: str):
        await self.bucket.download_fileobj(key, fp)

    async def delete_objects(self, key: str):
        await self.bucket.delete_objects(Delete={"Objects": [{"Key": key}]})

    async def list_files(self, prefix="") -> list[str]:
        return [obj.key async for obj in self.bucket.objects.filter(Prefix=prefix)]
