import unittest
import logging
from MuPythonLibrary.MuAnsiHandler import ColoredFormatter
from MuPythonLibrary.MuAnsiHandler import ColoredStreamHandler

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class MuAnsiHandlerTest(unittest.TestCase):

    # we are mainly looking for exception to be thrown

    def test_formatter(self):
        formatter = ColoredFormatter("%(levelname)s - %(message)s")
        record = logging.makeLogRecord({"name": "test", "level": logging.CRITICAL,
                                        "path": "test_path", "lineno": 0, "msg": "Test message"})
        output = formatter.format(record)
        self.assertNotEquals(output, None)
        CSI = '\033['
        if CSI not in output:
            self.fail("There was supposed to be a ANSI control code in that")

    def test_handler(self):
        stream = StringIO()
        # make sure we set out handler to strip the control sequence
        handler = ColoredStreamHandler(stream, strip=True)
        formatter = ColoredFormatter("%(levelname)s - %(message)s")
        handler.formatter = formatter
        record = logging.makeLogRecord({"name": "test", "level": logging.CRITICAL,
                                        "path": "test_path", "lineno": 0, "msg": "Test message"})
        handler.handle(record)
        # check for ANSI escape code in stream
        CSI = '\033['
        for line in stream.readlines():
            if CSI in line:
                self.fail("A control sequence was not stripped!")
