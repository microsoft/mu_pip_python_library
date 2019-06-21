## @file
# Script to generate Cat files for capsule update based on supplied inf file
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
import logging
from MuPythonLibrary.UtilityFunctions import RunCmd
from MuPythonLibrary.Windows.VsWhereUtilities import FindToolInWinSdk


class CatGenerator(object):
    SUPPORTED_OS = {'win10': '10',
                    '10': '10',
                    '10_au': '10_AU',
                    '10_rs2': '10_RS2',
                    '10_rs3': '10_RS3',
                    '10_rs4': '10_RS4',
                    'server10': 'Server10',
                    'server2016': 'Server2016',
                    'serverrs2': 'ServerRS2',
                    'serverrs3': 'ServerRS3',
                    'serverrs4': 'ServerRS4'
                    }

    def __init__(self, arch, os):
        self.Arch = arch
        self.OperatingSystem = os

    @property
    def Arch(self):
        return self._arch

    @Arch.setter
    def Arch(self, value):
        value = value.lower()
        if(value == "x64") or (value == "amd64"):  # support amd64 value so INF and CAT tools can use same arch value
            self._arch = "X64"
        elif(value == "arm"):
            self._arch = "ARM"
        elif(value == "arm64") or (value == "aarch64"):  # support UEFI defined aarch64 value as well
            self._arch = "ARM64"
        else:
            logging.critical("Unsupported Architecture: %s", value)
            raise ValueError("Unsupported Architecture")

    @property
    def OperatingSystem(self):
        return self._operatingsystem

    @OperatingSystem.setter
    def OperatingSystem(self, value):
        key = value.lower()
        if(key not in CatGenerator.SUPPORTED_OS.keys()):
            logging.critical("Unsupported Operating System: %s", key)
            raise ValueError("Unsupported Operating System")
        self._operatingsystem = CatGenerator.SUPPORTED_OS[key]

    def MakeCat(self, OutputCatFile, PathToInf2CatTool=None):
        # Find Inf2Cat tool
        if(PathToInf2CatTool is None):
            PathToInf2CatTool = FindToolInWinSdk("Inf2Cat.exe")
        # check if exists
        if not os.path.exists(PathToInf2CatTool):
            raise Exception("Can't find Inf2Cat on this machine.  Please install the Windows 10 WDK - "
                            "https://developer.microsoft.com/en-us/windows/hardware/windows-driver-kit")

        # Adjust for spaces in the path (when calling the command).
        if " " in PathToInf2CatTool:
            PathToInf2CatTool = '"' + PathToInf2CatTool + '"'

        OutputFolder = os.path.dirname(OutputCatFile)
        # Make Cat file
        cmd = "/driver:. /os:" + self.OperatingSystem + "_" + self.Arch + " /verbose"
        ret = RunCmd(PathToInf2CatTool, cmd, workingdir=OutputFolder)
        if(ret != 0):
            raise Exception("Creating Cat file Failed with errorcode %d" % ret)
        if(not os.path.isfile(OutputCatFile)):
            raise Exception("CAT file (%s) not created" % OutputCatFile)

        return 0
