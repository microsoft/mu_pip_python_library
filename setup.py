## @file setup.py
# This contains setup info for mu_python_library pip module
#
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

import setuptools
from setuptools.command.sdist import sdist
from setuptools.command.install import install
from setuptools.command.develop import develop
from MuPythonLibrary.Windows.VsWhereUtilities import _DownloadVsWhere

with open("README.rst", "r") as fh:
    long_description = fh.read()


class PostSdistCommand(sdist):
    """Post-sdist."""
    def run(self):
        # we need to download vswhere so throw the exception if we don't get it
        _DownloadVsWhere()
        sdist.run(self)


class PostInstallCommand(install):
    """Post-install."""
    def run(self):
        install.run(self)
        _DownloadVsWhere()


class PostDevCommand(develop):
    """Post-develop."""
    def run(self):
        develop.run(self)
        try:
            _DownloadVsWhere()
        except:
            pass


setuptools.setup(
    name="mu_python_library",
    author="Project Mu Team",
    author_email="maknutse@microsoft.com",
    description="Python library supporting Project Mu components (EDKII, TPM, Capsules, etc.)",
    long_description=long_description,
    url="https://github.com/microsoft/mu_pip_python_library",
    license='BSD2',
    packages=setuptools.find_packages(),
    cmdclass={
        'sdist': PostSdistCommand,
        'install': PostInstallCommand,
        'develop': PostDevCommand,
    },
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta"
    ]
)
