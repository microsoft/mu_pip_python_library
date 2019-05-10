## @file
# Test script for InfGenerator.py
#
# Copyright (c) 2019, Microsoft Corporation
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
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##

import unittest
from MuPythonLibrary.Uefi.Capsule.InfGenerator import InfGenerator

# must run from build env or set PYTHONPATH env variable to point to the MuPythonLibrary folder
# To run unit test open cmd prompt in the MuPythonLibrary folder
# and then run 'python -m unittest discover -p "*_test.py"'


class InfGeneratorTest(unittest.TestCase):
    VALID_GUID_STRING = "3cad7a0c-d35b-4b75-96b1-03a9fb07b7fc"

    def test_valid(self):
        o = InfGenerator("test_name", "provider", InfGeneratorTest.VALID_GUID_STRING, "x64",
                         "description", "aa.bb.cc.dd", "0xaabbccdd")
        self.assertIsInstance(o, InfGenerator)
        self.assertEqual(o.Name, "test_name")
        self.assertEqual(o.Provider, "provider")
        self.assertEqual(o.EsrtGuid, InfGeneratorTest.VALID_GUID_STRING)
        self.assertEqual(o.Arch, InfGenerator.SUPPORTED_ARCH["x64"])
        self.assertEqual(o.Description, "description")
        self.assertEqual(int(o.VersionHex, 0), int("0xaabbccdd", 0))
        self.assertEqual(o.VersionString, "aa.bb.cc.dd")
        self.assertEqual(o.Manufacturer, "provider")

        # loop thru all supported arch and make sure it works
        for a in InfGenerator.SUPPORTED_ARCH.keys():
            with self.subTest(Arch=a):
                o.Arch = a
                self.assertEqual(InfGenerator.SUPPORTED_ARCH[a], o.Arch)

        # set manufacturer
        o.Manufacturer = "manufacturer"
        self.assertEqual("manufacturer", o.Manufacturer)

    def test_invalid_name_symbol(self):

        InvalidChars = ['~', '`', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', ' ', '{', '[', '}', ']', '+', '=']
        for a in InvalidChars:
            with self.subTest(name="test{}name".format(a)):
                name = "test{}name".format(a)
                with self.assertRaises(ValueError):
                    InfGenerator(name, "provider", InfGeneratorTest.VALID_GUID_STRING, "x64",
                                 "description", "aa.bb", "0xaabbccdd")

    def test_version_string_format(self):
        with self.subTest(version_string="zero ."):
            with self.assertRaises(ValueError):
                InfGenerator("test_name", "provider", InfGeneratorTest.VALID_GUID_STRING, "x64",
                             "description", "1234", "0x100000000")

        with self.subTest(version_string="> 3 ."):
            with self.assertRaises(ValueError):
                InfGenerator("test_name", "provider", InfGeneratorTest.VALID_GUID_STRING, "x64",
                             "description", "1.2.3.4.5", "0x100000000")

    def test_version_hex_too_big(self):
        with self.subTest("hex string too big"):
            with self.assertRaises(ValueError):
                InfGenerator("test_name", "provider", InfGeneratorTest.VALID_GUID_STRING, "x64",
                             "description", "aa.bb", "0x100000000")

        with self.subTest("decimal too big"):
            with self.assertRaises(ValueError):
                InfGenerator("test_name", "provider", InfGeneratorTest.VALID_GUID_STRING, "x64",
                             "description", "aa.bb", "4294967296")

    def test_version_hex_can_support_decimal(self):
        o = InfGenerator("test_name", "provider", InfGeneratorTest.VALID_GUID_STRING, "x64",
                         "description", "aa.bb.cc.dd", "12356")
        self.assertEqual(int(o.VersionHex, 0), 12356)

    def test_invalid_guid_format(self):
        with self.assertRaises(ValueError):
            InfGenerator("test_name", "provider", "NOT A VALID GUID", "x64", "description", "aa.bb", "0x1000000")
