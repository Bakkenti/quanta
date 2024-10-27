import os
from django.core.files.storage import FileSystemStorage
from django.utils.crypto import get_random_string

class UniqueFilenameStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)

        while self.exists(name):
            name = os.path.join(dir_name, f"{file_root}_{get_random_string(6)}{file_ext}")

        return name
