import datetime
import time
from lark_oapi.api.drive.v1 import *
from .TenantManager import TenantManager
from modules.exceptions import FileUploadError
import os
import asyncio
from src.modules.lark import Lark
from loguru import logger
import requests

class FileManager:
    def __init__(self, lark_client: Lark, bitable_token: str):
        self.lark = lark_client.client
        self.bitable_token = bitable_token
        self.recording_directory = os.getenv("RECORDING_DIRECTORY") or "medias/recordings"
        self.semaphore = asyncio.Semaphore(4)

    def download_url(self, url, file_name):
        response = requests.get(url)

        if response.status_code == 200:
            with open(file_name, 'wb') as f:
                f.write(response.content)
            print(f"File downloaded successfully and saved as {file_name}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")

    def upload(self, file_path):
        if not os.path.exists(file_path):
            return
        filename = os.path.split(file_path)[1]
        file = open(file_path, 'rb')

        size = self.get_file_size(file_path)

        request: UploadAllMediaRequest = UploadAllMediaRequest.builder() \
            .request_body(UploadAllMediaRequestBody.builder()
                .file_name(filename)
                .parent_type("bitable_file")
                .parent_node(self.bitable_token)
                .size(size)
                .file(file)
                .build()) \
            .build()

        response: UploadAllMediaResponse = self.lark.drive.v1.media.upload_all(request)

        if response.code != 0:
            raise FileUploadError(
                code=response.code, 
                message=response.msg, 
                file_path=file_path
            )

        return response.data.file_token

    def get_file_size(self, filepath):
        try:
            with open(filepath, 'rb') as file:
                file.seek(0, 2)  # Move the file pointer to the end of the file
                file_size = file.tell()  # Get the current position, which is the file size
                return file_size
        except FileNotFoundError:
            return None