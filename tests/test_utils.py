""" Test internal utilities """
from os import chmod
from os.path import isdir, isfile
from stat import S_IREAD
from unittest import TestCase

from botlet.utils import SafeTemporaryDirectory, SafeQueue

class TestUtils(TestCase):
    """ Test suite for utility methods """
    def test_tempdir(self):
        """ Check a temporary directory with files inside works """
        with SafeTemporaryDirectory(prefix='test_') as dir_path:
            self.assertTrue(isdir(dir_path))
            file_path = dir_path + '/test'
            open(file_path, 'w').close()
            self.assertTrue(isfile(file_path))
            # Test permission to delete read-only files
            chmod(file_path, S_IREAD)
        self.assertFalse(isdir(dir_path))

    def test_queue(self):
        """ Fill and empty queue with restrictions """
        queue = SafeQueue[int](2)
        self.assertIsNone(queue.get())
        self.assertTrue(queue.put(1))
        self.assertTrue(queue.put(2))
        self.assertFalse(queue.put(3))
        self.assertEqual(queue.get(), 1)
        self.assertEqual(queue.get(), 2)
        self.assertIsNone(queue.get())
