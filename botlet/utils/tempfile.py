""" Convenience temporary files """
from os import chmod
from stat import S_IWRITE
from tempfile import TemporaryDirectory
from shutil import rmtree


class SafeTemporaryDirectory(TemporaryDirectory):
    """ Like TemporaryDirectory but with safe deletion on windows """
    def cleanup(self):
        try:
            super().cleanup()
        except PermissionError:
            # Windows fix, see <https://docs.python.org/3/library/shutil.html#rmtree-example>
            def remove_readonly(func, path, _):
                chmod(path, S_IWRITE)
                func(path)
            rmtree(self.name, onerror=remove_readonly)
