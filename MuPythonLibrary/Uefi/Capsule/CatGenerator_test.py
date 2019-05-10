## @file
# Test script for CatGenerator.py based on various architecture/OS
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

import os
import unittest
from MuPythonLibrary.Uefi.Capsule.CatGenerator import CatGenerator

# must run from build env or set PYTHONPATH env variable to point to the MuPythonLibrary folder


class CatGeneratorTest(unittest.TestCase):

    def test_win10_OS(self):
        o = CatGenerator("x64", "win10")
        self.assertEqual(o.OperatingSystem, "10")

    def test_10_OS(self):
        o = CatGenerator("x64", "10")
        self.assertEqual(o.OperatingSystem, "10")

    def test_10_AU_OS(self):
        o = CatGenerator("x64", "10_AU")
        self.assertEqual(o.OperatingSystem, "10_AU")

    def test_10_RS2_OS(self):
        o = CatGenerator("x64", "10_RS2")
        self.assertEqual(o.OperatingSystem, "10_RS2")

    def test_10_RS3_OS(self):
        o = CatGenerator("x64", "10_RS3")
        self.assertEqual(o.OperatingSystem, "10_RS3")

    def test_10_RS4_OS(self):
        o = CatGenerator("x64", "10_RS4")
        self.assertEqual(o.OperatingSystem, "10_RS4")

    def test_win10Server_OS(self):
        o = CatGenerator("x64", "Server10")
        self.assertEqual(o.OperatingSystem, "Server10")

    def test_Server2016_OS(self):
        o = CatGenerator("x64", "Server2016")
        self.assertEqual(o.OperatingSystem, "Server2016")

    def test_ServerRS2_OS(self):
        o = CatGenerator("x64", "ServerRS2")
        self.assertEqual(o.OperatingSystem, "ServerRS2")

    def test_ServerRS3_OS(self):
        o = CatGenerator("x64", "ServerRS3")
        self.assertEqual(o.OperatingSystem, "ServerRS3")

    def test_ServerRS4_OS(self):
        o = CatGenerator("x64", "ServerRS4")
        self.assertEqual(o.OperatingSystem, "ServerRS4")

    def test_invalid_OS(self):
        with self.assertRaises(ValueError):
            CatGenerator("x64", "Invalid Junk")

    def test_x64_arch(self):
        o = CatGenerator("x64", "win10")
        self.assertEqual(o.Arch, "X64")

    def test_amd64_arch(self):
        o = CatGenerator("amd64", "win10")
        self.assertEqual(o.Arch, "X64")

    def test_arm_arch(self):
        o = CatGenerator("arm", "win10")
        self.assertEqual(o.Arch, "ARM")

    def test_arm64_arch(self):
        o = CatGenerator("arm64", "win10")
        self.assertEqual(o.Arch, "ARM64")

    def test_aarch64_arch(self):
        o = CatGenerator("aarch64", "win10")
        self.assertEqual(o.Arch, "ARM64")

    def test_invalid_arch(self):
        with self.assertRaises(ValueError):
            CatGenerator("Invalid Arch", "win10")

    def test_invalid_pathtotool(self):
        o = CatGenerator("amd64", "10")
        with self.assertRaises(Exception) as cm:
            o.MakeCat("garbage", os.path.join("c:", "test", "badpath", "inf2cat.exe"))
        self.assertTrue(str(cm.exception).startswith("Can't find Inf2Cat on this machine."))
