import os
import uuid
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible

@deconstructible
class CustomStorage(FileSystemStorage):
    def __init__(self, location, base_url):
        super().__init__(location=location, base_url=base_url)

    def get_available_name(self, name, max_length=None):
        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)
        unique_name = f"{file_root}_{uuid.uuid4().hex[:8]}{file_ext}"
        return os.path.join(dir_name, unique_name)

video_storage = CustomStorage(location="media/lesson_videos/", base_url="/media/lesson_videos/")

image_storage = CustomStorage(location="media/lesson_images/", base_url="/media/lesson_images/")

avatar_storage = CustomStorage(location="media/avatars/", base_url="/media/avatars/")
