import asyncio
import io
import os

from dotenv import load_dotenv

from bacchilu_aios3 import Bucket

load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")

S3_BUCKET = "life365"
REGION_NAME = "eu-central-1"


async def go():
    async with Bucket.create_obj(
        S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION_NAME
    ) as bucket:
        with io.BytesIO(b"Nel mezzo del cammin di nostra vita") as fp:
            await bucket.upload_fileobj(fp, "TEST/test.py")
        with io.BytesIO() as fp:
            await bucket.download_fileobj(fp, "TEST/test.py")
            print(fp.getvalue())
        print(await bucket.list_files("TEST"))
        await bucket.delete_objects("TEST/test.py")


if __name__ == "__main__":
    asyncio.run(go())
