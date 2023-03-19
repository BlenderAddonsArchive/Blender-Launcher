from pathlib import Path

from modules._copyfileobj import copyfileobj
from modules.settings import get_library_folder
from PyQt6.QtCore import QThread, pyqtSignal


class Downloader(QThread):
    started = pyqtSignal()
    progress_changed = pyqtSignal(
        'PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')
    finished = pyqtSignal('PyQt_PyObject')

    def __init__(self, manager, link):
        QThread.__init__(self)
        self.manager = manager
        self.link = link
        self.size = 0

    def run(self):
        self.progress_changed.emit(0, 0, "Downloading")
        self.started.emit()

        temp_folder = Path(get_library_folder()) / ".temp"

        # Create temp directory
        if not temp_folder.is_dir():
            temp_folder.mkdir()

        dist = temp_folder / Path(self.link).name

        with self.manager.request('GET',
                                  self.link,
                                  preload_content=False) as r:
            self.size = int(r.headers['Content-Length'])

            with open(dist, 'wb') as f:
                copyfileobj(r, f, self.set_progress)

        r.release_conn()
        r.close()

        self.finished.emit(dist)
        return

    def set_progress(self, obtained):
        self.progress_changed.emit(obtained, self.size, "Downloading")
