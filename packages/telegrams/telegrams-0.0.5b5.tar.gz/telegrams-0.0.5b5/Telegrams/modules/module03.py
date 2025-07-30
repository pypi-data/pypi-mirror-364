from ..exceptions import CatboxError
from ..functions import edit_album
from ..functions import upload_file
from ..functions import delete_album
from ..functions import upload_album
from ..functions import delete_files
from ..functions import create_album
from ..functions import upload_to_litterbox

class Catbox:

    def __init__(self, userhash=None):
        self.userhash = userhash
    
    def upload_file(self, file_path, timeout=30):
        return upload_file(file_path, timeout, self.userhash)

    def upload_to_litterbox(self, file_path, time='1h', timeout=30):
        return upload_to_litterbox(file_path, time, timeout)

    def upload_album(self, file_paths, timeout=30):
        return upload_album(file_paths, timeout, self.userhash)

    def delete_files(self, files):
        if not self.userhash:
            raise CatboxError("Userhash is required to delete files.")
        return delete_files(files, self.userhash)

    def create_album(self, files, title, description):
        if not self.userhash:
            raise CatboxError("Userhash is required to create an album.")
        return create_album(files, title, description, self.userhash)

    def edit_album(self, shortcode, files, title, description):
        if not self.userhash:
            raise CatboxError("Userhash is required to edit an album.")
        return edit_album(shortcode, files, title, description, self.userhash)

    def delete_album(self, shortcode):
        if not self.userhash:
            raise CatboxError("Userhash is required to delete an album.")
        return delete_album(shortcode, self.userhash)
