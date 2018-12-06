# @file MuAnsiHandler.py
# Handle basic logging outputting to markdown
##
# Copyright (c) 2018, Microsoft Corporation
#
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCEOR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
##
import logging


class MarkdownFileHandler(logging.FileHandler):
    def __init__(self, filename, mode='a'):
        logging.FileHandler.__init__(self, filename, mode=mode)
        if self.stream.writable:
            self.stream.write("# Build Report\n [Go to table of contents](#table-of-contents)\n=====\n")
        self.contents = []

    def emit(self, record):
        if self.stream is None:
            self.stream = self._open()
        msg = record.message.strip("#- ")

        if len(msg) > 0:
            if logging.getLevelName(record.levelno) is "SECTION":
                self.contents.append((msg, []))
                msg = "## " + msg
            elif record.levelno == logging.CRITICAL:
                section_index = len(self.contents) - 1
                if section_index >= 0:
                    self.contents[section_index][1].append(msg)
                msg = "### " + msg
            elif record.levelno == logging.ERROR:
                msg = "#### " + msg
            elif record.levelno == logging.WARNING:
                msg = "  _" + msg + "_"
            else:
                msg = "    " + msg
            stream = self.stream
            # issue 35046: merged two stream.writes into one.
            stream.write(msg + self.terminator)

            # self.flush()

    @staticmethod
    def __convert_to_markdownlink(text):
        # Using info from here https://stackoverflow.com/a/38507669
        # get rid of uppercase characters
        text = text.lower().strip()
        # get rid of punctuation
        text = text.replace(".", "").replace(",", "").replace("-", "")
        # replace spaces
        text = text.replace(" ", "-")
        return text

    def close(self):
        self.stream.write("## Table of Contents\n")
        for item, subsections in self.contents:
            link = MarkdownFileHandler.__convert_to_markdownlink(item)
            self.stream.write("+ [{0}](#{1})\n".format(item, link))
            for section in subsections:
                section_link = MarkdownFileHandler.__convert_to_markdownlink(section)
                self.stream.write("  + [{0}](#{1})\n".format(section, section_link))

        self.flush()
