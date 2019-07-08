# @file VsWhereUtilities_test.py
# Unit test harness for the VsWhereUtilities module/classes.
#
##
# Copyright (c), Microsoft Corporation
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
import sys
import os
import MuPythonLibrary.Windows.VsWhereUtilities as VWU


class TestVsWhere(unittest.TestCase):

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_GetVsWherePath(self):
        # Gets VSWhere
        old_vs_path = VWU.GetVsWherePath()
        os.remove(old_vs_path)
        self.assertFalse(os.path.isfile(old_vs_path), "This should be deleted")
        vs_path = VWU.GetVsWherePath()
        self.assertTrue(os.path.isfile(vs_path), "This should be back")

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_FindWithVsWhere(self):
        # Finds something with VSWhere
        ret, star_prod = VWU.FindWithVsWhere()
        self.assertEqual(ret, 0, "Return code should be zero")
        self.assertNotEqual(star_prod, None, "We should have found this product")
        ret, bad_prod = VWU.FindWithVsWhere("bad_prod")
        self.assertEqual(ret, 0, "Return code should be zero")
        self.assertEqual(bad_prod, None, "We should not have found this product")

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_QueryVcVariables(self):
        keys = ["VCINSTALLDIR", "WindowsSDKVersion"]
        results = VWU.QueryVcVariables(keys)

        self.assertIsNotNone(results["VCINSTALLDIR"])
        self.assertIsNotNone(results["WindowsSDKVersion"])

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_FindToolInWinSdk(self):
        results = VWU.FindToolInWinSdk("signtool.exe")
        self.assertIsNotNone(results)
        self.assertTrue(os.path.isfile(results))
        results = VWU.FindToolInWinSdk("this_tool_should_never_exist.exe")
        self.assertIsNone(results)


if __name__ == '__main__':
    unittest.main()
