import unittest
import logging
from MuPythonLibrary.MuAnsiHandler import ColoredFormatter
from MuPythonLibrary.MuAnsiHandler import ColoredStreamHandler

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class MuAnsiHandlerTest(unittest.TestCase):

    def test_formatter(self):
        formatter = ColoredFormatter()
        record = logging.LogRecord("test", logging.DEBUG, "test_path", 0, "Test message")
        output = formatter.format(record)
        self.assertNotEquals(output, None)

    def test_handler(self):
        stream = StringIO()
        handler = ColoredStreamHandler(stream, strip=True)
        formatter = ColoredFormatter()
        handler.formatter = formatter
        record = logging.LogRecord("test", logging.CRITICAL, "test_path", 0, "Test message")
        handler.handle(record)
