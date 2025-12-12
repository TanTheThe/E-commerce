from supabase import Client, create_client
import os
from src.config import Config

supabase_client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
bucket_name = Config.BUCKET_NAME

class ImageRepository:
    def __init__(self):
        self.supabase = supabase_client
        self.bucket_name = bucket_name


    async def upload_file(self, file_path: str, file_content: bytes, content_type: str):
        try:
            response = self.supabase.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={
                    "content-type": content_type,
                    "upsert": "false"
                }
            )
            return response
        except Exception as e:
            raise e


    async def delete_file(self, file_path: str):
        try:
            response = self.supabase.storage.from_(self.bucket_name).remove([file_path])
            return response
        except Exception as e:
            raise e


    async def list_files(self, folder_path: str):
        try:
            response = self.supabase.storage.from_(self.bucket_name).list(folder_path)
            return response
        except Exception as e:
            return []


    async def check_file_exists(self, file_path: str):
        try:
            folder = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            files = await self.list_files(folder)

            return any(file['name'] == filename for file in files)
        except Exception:
            return False


    def get_public_url(self, file_path: str):
        return self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)