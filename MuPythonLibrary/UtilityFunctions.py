#
# Utility Functions to support re-use in python scripts.
##
# Includes functions for running external commands, etc
##
# Copyright Microsoft Corporation, 2017
##
from __future__ import print_function  # support Python3 and 2 for print
import os
import logging
import datetime
import shutil
import threading
import subprocess
import sys
import platform
from collections import namedtuple

####
# Helper to allow Enum type to be used which allows better code readability
#
# ref: http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
####


class Enum(tuple):
    __getattr__ = tuple.index


####
# Class to support running commands from the shell in a python environment.
# Don't use directly.
#
# PropagatingThread copied from sample here:
# https://stackoverflow.com/questions/2829329/catch-a-threads-exception-in-the-caller-thread-in-python
####
class PropagatingThread(threading.Thread):
    def run(self):
        self.exc = None
        try:
            if hasattr(self, '_Thread__target'):
                # Thread uses name mangling prior to Python 3.
                self.ret = self._Thread__target(*self._Thread__args, **self._Thread__kwargs)
            else:
                self.ret = self._target(*self._args, **self._kwargs)
        except BaseException as e:
            self.exc = e

    def join(self, timeout=None):
        super(PropagatingThread, self).join()
        if self.exc:
            raise self.exc
        return self.ret


####
# Helper functions for running commands from the shell in python environment
# Don't use directly
#
# process output stream and write to log.
# part of the threading pattern.
#
#  http://stackoverflow.com/questions/19423008/logged-subprocess-communicate
####
def reader(filepath, outstream, stream, logging_level=logging.INFO):
    f = None
    # open file if caller provided path
    if(filepath):
        f = open(filepath, "w")

    while True:
        s = stream.readline().decode()
        if not s:
            break
        if(f is not None):
            # write to file if caller provided file
            f.write(s)
        if(outstream is not None):
            # write to stream object if caller provided object
            outstream.write(s)
        logging.log(logging_level, s.rstrip())
    stream.close()
    if(f is not None):
        f.close()

####
# Add mono to front of command and resolve full path of exe for mono,
# Used to add nuget support on posix platforms.
# https://docs.microsoft.com/en-us/nuget/install-nuget-client-tools
#
# @return list containing either ["nuget.exe"] or ["mono", "/PATH/TO/nuget.exe"]
####


def GetNugetCmd():
    file = "NuGet.exe"
    cmd = []
    if (GetHostInfo().os == "Linux"):
        cmd += ["mono"]
        found = False
        for env_var in os.getenv("PATH").split(os.pathsep):
            env_var = os.path.join(os.path.normpath(env_var), file)
            if os.path.isfile(env_var):
                file = '"' + env_var + '"'
                logging.info("File was found on the path: %s" % file)
                found = True
                break
        if not found:
            raise Exception("NuGet.exe not found on path")
    cmd += [file]
    return cmd


####
# Returns a namedtuple containing information about host machine.
#
# @return namedtuple Host(os=OS Type, arch=System Architecture, bit=Highest Order Bit)
####
def GetHostInfo():
    Host = namedtuple('Host', 'os arch bit')
    host_info = platform.uname()
    os = host_info.system
    processor_info = host_info.machine
    logging.debug("Getting host info for host: {0}".format(str(host_info)))

    arch = None
    bit = None

    if ("x86" in processor_info) or ("AMD" in processor_info) or ("Intel" in processor_info):
        arch = "x86"
    elif ("ARM" in processor_info) or ("AARCH" in processor_info):
        arch = "ARM"

    if "32" in processor_info:
        bit = "32"
    elif "64" in processor_info:
        bit = "64"

    if (arch is None) or (bit is None):
        raise EnvironmentError("Host info could not be parsed: {0}".format(str(host_info)))

    return Host(os=os, arch=arch, bit=bit)


####
# Run a shell commmand and print the output to the log file
# This is the public function that should be used to run commands from the shell in python environment
# @param cmd - command being run, either quoted or not quoted
# @param parameters - parameters string taken as is
# @param capture - boolean to determine if caller wants the output captured in any format.
# @param workingdir - path to set to the working directory before running the command.
# @param outfile - capture output to file of given path.
# @param outstream - capture output to a stream.
# @param environ - shell environment variables dictionary that replaces the one inherited from the
#                  current process.
#
# @return returncode of called cmd
####
def RunCmd(cmd, parameters, capture=True, workingdir=None, outfile=None, outstream=None, environ=None,
           logging_level=logging.INFO, raise_exception_on_nonzero=False):
    cmd = cmd.strip('"\'')
    if " " in cmd:
        cmd = '"' + cmd + '"'
    if parameters is not None:
        parameters = parameters.strip()
        cmd += " " + parameters
    starttime = datetime.datetime.now()
    logging.log(logging_level, "Cmd to run is: " + cmd)
    logging.log(logging_level, "------------------------------------------------")
    logging.log(logging_level, "--------------Cmd Output Starting---------------")
    logging.log(logging_level, "------------------------------------------------")
    c = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=workingdir, shell=True, env=environ)
    if(capture):
        outr = PropagatingThread(target=reader, args=(outfile, outstream, c.stdout, logging_level))
        outr.start()
        c.wait()
        outr.join()
    else:
        c.wait()

    endtime = datetime.datetime.now()
    delta = endtime - starttime
    endtime_str = "{0[0]:02}:{0[1]:02}".format(divmod(delta.seconds, 60))
    logging.log(logging_level, "------------------------------------------------")
    logging.log(logging_level, "--------------Cmd Output Finished---------------")
    logging.log(logging_level, "--------- Running Time (mm:ss): " + endtime_str + " ----------")
    logging.log(logging_level, "------------------------------------------------")

    if raise_exception_on_nonzero and c.returncode != 0:
        raise Exception("{0} failed with error code: {1}".format(cmd, c.returncode))
    return c.returncode

####
# Run a python script and print the output to the log file
# This is the public function that should be used to execute python scripts from the shell in python environment.
# The python script will be located using the path as if it was an executable.
#
# @param cmd - cmd string to run including parameters
# @param capture - boolean to determine if caller wants the output captured in any format.
# @param workingdir - path to set to the working directory before running the command.
# @param outfile - capture output to file of given path.
# @param outstream - capture output to a stream.
# @param environ - shell environment variables dictionary that replaces the one inherited from the
#                  current process.
#
# @return returncode of called cmd
####


def RunPythonScript(pythonfile, params, capture=True, workingdir=None, outfile=None, outstream=None, environ=None):
    # locate python file on path
    pythonfile.strip('"\'')
    if " " in pythonfile:
        pythonfile = '"' + pythonfile + '"'
    params.strip()
    logging.debug("RunPythonScript: {0} {1}".format(pythonfile, params))
    if(os.path.isabs(pythonfile)):
        logging.debug("Python Script was given as absolute path: %s" % pythonfile)
    elif(os.path.isfile(os.path.join(os.getcwd(), pythonfile))):
        pythonfile = os.path.join(os.getcwd(), pythonfile)
        logging.debug("Python Script was given as relative path: %s" % pythonfile)
    else:
        # loop thru path environment variable
        for a in os.getenv("PATH").split(os.pathsep):
            a = os.path.normpath(a)
            if os.path.isfile(os.path.join(a, pythonfile)):
                pythonfile = os.path.join(a, pythonfile)
                logging.debug("Python Script was found on the path: %s" % pythonfile)
                break
    params = pythonfile + " " + params
    return RunCmd(sys.executable, params, capture=capture, workingdir=workingdir, outfile=outfile,
                  outstream=outstream, environ=environ)
####
# Locally Sign input file using Windows SDK signtool.  This will use a local Pfx file.
# WARNING!!! : This should not be used for production signing as that process should follow stronger
#               security practices (HSM / smart cards / etc)
#
#  Signing is in format specified by UEFI authentacted variables
####


def DetachedSignWithSignTool(SignToolPath, ToSignFilePath, SignatureOutputFile, PfxFilePath,
                             PfxPass=None, Oid="1.2.840.113549.1.7.2", Eku=None):

    # check signtool path
    if not os.path.exists(SignToolPath):
        logging.error("Path to signtool invalid.  %s" % SignToolPath)
        return -1

    # Adjust for spaces in the path (when calling the command).
    if " " in SignToolPath:
        SignToolPath = '"' + SignToolPath + '"'

    OutputDir = os.path.dirname(SignatureOutputFile)
    # Signtool docs https://docs.microsoft.com/en-us/dotnet/framework/tools/signtool-exe
    # Signtool parameters from
    #   https://docs.microsoft.com/en-us/windows-hardware/manufacture/desktop/secure-boot-key-generation-and-signing-using-hsm--example  # noqa: E501
    # Search for "Secure Boot Key Generation and Signing Using HSM"
    params = 'sign /fd sha256 /p7ce DetachedSignedData /p7co ' + Oid + ' /p7 "' + \
             OutputDir + '" /f "' + PfxFilePath + '"'
    if Eku is not None:
        params += ' /u ' + Eku
    if PfxPass is not None:
        # add password if set
        params = params + ' /p ' + PfxPass
    params = params + ' /debug /v "' + ToSignFilePath + '" '
    ret = RunCmd(SignToolPath, params)
    if(ret != 0):
        logging.error("Signtool failed %d" % ret)
        return ret
    signedfile = os.path.join(OutputDir, os.path.basename(ToSignFilePath) + ".p7")
    if(not os.path.isfile(signedfile)):
        raise Exception("Output file doesn't eixst %s" % signedfile)

    shutil.move(signedfile, SignatureOutputFile)
    return ret

####
# Locally Sign input file using Windows SDK signtool.  This will use a local Pfx file.
# WARNING!!! : This should not be used for production signing as that process should follow
#              stronger security practices (HSM / smart cards / etc)
#
#  Signing is catalog format which is an attached signature
####


def CatalogSignWithSignTool(SignToolPath, ToSignFilePath, PfxFilePath, PfxPass=None):

    # check signtool path
    if not os.path.exists(SignToolPath):
        logging.error("Path to signtool invalid.  %s" % SignToolPath)
        return -1

    # Adjust for spaces in the path (when calling the command).
    if " " in SignToolPath:
        SignToolPath = '"' + SignToolPath + '"'

    OutputDir = os.path.dirname(ToSignFilePath)
    # Signtool docs https://docs.microsoft.com/en-us/dotnet/framework/tools/signtool-exe
    # todo: link to catalog signing documentation
    params = "sign /a /fd SHA256 /f " + PfxFilePath
    if PfxPass is not None:
        # add password if set
        params = params + ' /p ' + PfxPass
    params = params + ' /debug /v "' + ToSignFilePath + '" '
    ret = RunCmd(SignToolPath, params, workingdir=OutputDir)
    if(ret != 0):
        logging.error("Signtool failed %d" % ret)
    return ret


###
# Function to print a byte list as hex and optionally output ascii as well as
# offset within the buffer
###
def PrintByteList(ByteList, IncludeAscii=True, IncludeOffset=True, IncludeHexSep=True, OffsetStart=0):
    Ascii = ""
    for index in range(len(ByteList)):
        # Start of New Line
        if(index % 16 == 0):
            if(IncludeOffset):
                print("0x%04X -" % (index + OffsetStart), end='')

        # Midpoint of a Line
        if(index % 16 == 8):
            if(IncludeHexSep):
                print(" -", end='')

        # Print As Hex Byte
        print(" 0x%02X" % ByteList[index], end='')

        # Prepare to Print As Ascii
        if(ByteList[index] < 0x20) or (ByteList[index] > 0x7E):
            Ascii += "."
        else:
            Ascii += ("%c" % ByteList[index])

        # End of Line
        if(index % 16 == 15):
            if(IncludeAscii):
                print(" %s" % Ascii, end='')
            Ascii = ""
            print("")

    # Done - Lets check if we have partial
    if(index % 16 != 15):
        # Lets print any partial line of ascii
        if(IncludeAscii) and (Ascii != ""):
            # Pad out to the correct spot

            while(index % 16 != 15):
                print("     ", end='')
                if(index % 16 == 7):  # acount for the - symbol in the hex dump
                    if(IncludeOffset):
                        print("  ", end='')
                index += 1
            # print the ascii partial line
            print(" %s" % Ascii, end='')
            # print a single newline so that next print will be on new line
        print("")


if __name__ == '__main__':
    pass
    # Test code for printing a byte buffer
    # a = [0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x3b, 0x3c, 0x3d]
    # index = 0x55
    # while(index < 0x65):
    #     a.append(index)
    #     PrintByteList(a)
    #     index += 1
