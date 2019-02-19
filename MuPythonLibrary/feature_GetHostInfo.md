# GetHostInfo

This document details the utility function called GetHostInfo. This function was written because NuGet needed a way to determine attributes about the host system to determine what parts of a dependency to use.

## How to Use
```python
from MuPythonLibrary.UtilityFunctions import GetHostInfo

host_info = GetHostInfo()
```

## Usage info

GetHostInfo() will return a namedtuple with 3 attributes describing the host machine. Below for each is the name of the field, description of the field and possible contents therein.

### 1. os - OS Name

  Windows, Linux, or Java

### 2. arch - Processor architecture

  ARM or x86

### 3. bit - Highest order bit

  32 or 64

## Purpose

  Since there are multiple different ways one could derive these values, it is necessary provide a common implementation of that logic to ensure it is uniform.