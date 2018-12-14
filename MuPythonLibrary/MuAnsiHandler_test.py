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
        record = logging.makeLogRecord({"name": "", "level": logging.CRITICAL, "levelno": logging.CRITICAL,
                                        "levelname": "CRITICAL", "path": "test_path", "lineno": 0,
                                        "msg": "Test message"})
        output = formatter.format(record)
        self.assertNotEqual(output, None)
        CSI = '\033['
        self.assertGreater(len(output), 0, "We should have some output")
        self.assertFalse((CSI not in output), "There was supposed to be a ANSI control code in that %s" % output)

    def test_handler(self):
        stream = StringIO()
        # make sure we set out handler to strip the control sequence
        handler = ColoredStreamHandler(stream, strip=True, convert=False)
        formatter = ColoredFormatter("%(levelname)s - %(message)s")
        handler.formatter = formatter
        handler.level = logging.NOTSET
        record = logging.makeLogRecord({"name": "", "level": logging.INFO, "levelno": logging.INFO,
                                        "levelname": "INFO", "path": "test_path", "lineno": 0,
                                        "msg": "Test message"})

        record2 = logging.makeLogRecord({"name": "", "level": logging.CRITICAL, "levelno": logging.CRITICAL,
                                         "levelname": "CRITICAL", "path": "test_path", "lineno": 0,
                                         "msg": "Test message"})
        handler.emit(record)
        handler.flush()

        # check for ANSI escape code in stream
        CSI = '\033['
        stream.seek(0)
        lines = stream.readlines()
        self.assertGreater(len(lines), 0, "We should have some output %s" % lines)
        for line in lines:
            if CSI in line:
                self.fail("A control sequence was not stripped! %s" % lines)

        stream = StringIO()

        handler = ColoredStreamHandler(stream, strip=False, convert=False)
        handler.formatter = formatter
        handler.level = logging.NOTSET

        handler.emit(record2)
        handler.flush()

        found_csi = False
        stream.seek(0)
        lines = stream.readlines()
        self.assertGreater(len(lines), 0, "We should have some output %s" % lines)
        for line in lines:
            if CSI in line:
                found_csi = True
        self.assertTrue(found_csi, "We are supposed to to have found an ANSI control character %s" % lines)
