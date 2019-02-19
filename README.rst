=================
MU Python Library
=================
.. |build_status_windows| image:: https://dev.azure.com/projectmu/mu%20pip/_apis/build/status/PythonLibrary/Mu%20Pip%20Python%20Library%20-%20PR%20Gate%20(Windows)?branchName=master
.. |build_status_linux| image:: https://dev.azure.com/projectmu/mu%20pip/_apis/build/status/PythonLibrary/Mu%20Pip%20Python%20Library%20-%20PR%20Gate%20(Linux%20-%20Ubuntu%201604)?branchName=master

|build_status_windows| Current build status for master on Windows

|build_status_linux| Current build status for master on Linux

About
=====

Python files describing various miscellaneous components from the TPM and EDKII specs.
Please see Project Mu for details https://microsoft.github.io/mu

Version History
===============

0.4.3-dev
-----

Main Changes:

- Added GetHostInfo to UtilityFunctions. This function will parse the platform module to provide information about the host.
- Added colors for progress and section labels.

0.4.2
-----

Bug fix around quoted paths for Nuget

0.4.1
-----

Main changes:

- Keep track of errors that occur during the build process and display the list at the very end to make errors easier to locate in the log.
- Added a filter, which gets evaluated before level, that allows specific modules to either be raised or lowered in level before being output to the log.

Bug fixes:

- Change FileHandler mode to avoid appending a new log to an existing log.
- Change MuMarkdownHanlder close routine to avoid writing the table of contents twice.
- Change NuGet.exe case to match the executable exactly.
- On Posix systems, throw exception if NuGet.exe is not found on the path instead of failing silently.

0.4.0
-----

Main changes:

- Add the OverrideParser class and tests.
- Update DscParser to include the enhanced provenance.

Bug fixes:

- Clean up the README.rst file.
- Update CI pipeline to report flake results more conveniently.

0.3.1
-----

Bug fixes to enable module to pass both sets of CI gates (Windows and Linux).

0.3.0
-----

Updated documentation and release process.  Transition to Beta.

< 0.3.0
-------

Alpha development
