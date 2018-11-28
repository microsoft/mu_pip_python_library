=================
MU Python Library
=================

About
==============

Python files describing various miscellaneous components from the TPM and EDKII specs.

Version History
===============

0.2.8
-----------------

Adding support for environment variables dictionary to RunCmd and RunPythonScript

0.2.7
-----------------

un-reverting 0.2.4: Using sys.executable in RunPythonScript instead of "python.exe" and assuming its on the path

0.2.6
-----------------

Fixing parameter parsing in RunPythonScript to preserve formatting of parameters

0.2.5
-----------------

Fixing parameters none check in RunCmd

0.2.4
-----------------

Using sys.executable in RunPythonScript instead of "python.exe" and assuming its on the path

0.2.3
-----------------

Conditionally adding quotes instead of automatically in RunCmd and RunPythonScript

0.2.2
-----------------

Fixing CatalogSignWithSignTool to use new RunCmd format

0.2.1
-----------------

Fixing RunPythonScript function to reference updated parameters

0.2.0
-----------------

Initial commit