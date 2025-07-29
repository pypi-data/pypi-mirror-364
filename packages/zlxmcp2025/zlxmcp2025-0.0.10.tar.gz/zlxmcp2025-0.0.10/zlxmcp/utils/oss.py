from oss2 import AuthV4, Bucket, ObjectIterator
from oss2.exceptions import OssError
from itertools import islice
from typing import Optional, Tuple, List


__all__ = [
    "OSS",
]


class OSS:
    def __init__(
            self,
            access_key_id: str,
            access_key_secret: str,
            bucket_name: str,
            region: str = "cn-hangzhou",
            expiration: int = 1850000,
            endpoint: str = "oss-cn-hangzhou.aliyuncs.com",
    ):
        """"""
        self.region = region
        self.expiration = expiration
        self.endpoint = endpoint
        self.bucket_name = bucket_name
        self.support_cname = False
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret

        self.bucket = Bucket(
            auth=AuthV4(self.access_key_id, self.access_key_secret),
            endpoint=self.endpoint, bucket_name=self.bucket_name, region=self.region
        )

    def download_file(self, object_name: str) -> Tuple[str, bytes]:
        """下载文件"""
        content = None
        try:
            file_obj = self.bucket.get_object(object_name)
            content = file_obj.read()
            msg = f"[{__class__.__name__}] Downloaded file: {object_name}"
        except OssError as e:
            msg = f"[{__class__.__name__}] Failed to download file: {e}"
        return msg, content

    def object_exist(self, object_name: str) -> Tuple[str, bool]:
        """查找文件是否存在"""
        is_exist = self.bucket.object_exists(object_name)
        msg = f"[{__class__.__name__}] File {object_name} exists: {is_exist}"
        return msg, is_exist

    def list_objects(
            self,
            prefix: Optional[str] = None,
            n: int = 10,
    ) -> Tuple[str, List[str]]:
        """列出文件"""
        msg = ""
        keys = []

        try:
            objects = list(islice(ObjectIterator(self.bucket, prefix=prefix), n))
            for obj in objects:
                keys.append(obj.key)
                msg += f"[OSS] {obj.key}\n"
        except OssError as e:
            msg = f"[{__class__.__name__}] Failed to list objects: {e}"
        return msg, keys

    def put_file(
            self,
            object_name: Optional[str] = None,
            data: Optional[bytes] = None
    ) -> Tuple[str, None]:
        """上传文件"""
        try:
            result = self.bucket.put_object(object_name, data)
            msg = f"[{__class__.__name__}] Uploaded successfully, status code: {result.status}."
        except OssError as e:
            msg = f"[{__class__.__name__}] Failed to upload file: {e}."
        return msg, None

    def sign_url(
            self,
            key: Optional[str],
            method: str = "GET",
            expires: int = 60
    ) -> Tuple[str, Optional[str]]:
        """将文件生成一个临时下载链接"""
        _, is_exist = self.object_exist(object_name=key)
        print(is_exist)
        url = None
        if not is_exist:
            msg = f"[{__class__.__name__}] Object {key} does not exist."
        else:
            msg = f"[{__class__.__name__}] Object {key} exists."
            url = self.bucket.sign_url(method=method, key=key, expires=expires)
        return msg, url
