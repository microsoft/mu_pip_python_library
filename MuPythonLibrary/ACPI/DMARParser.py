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
#
# Python script that converts a raw DMAR table into a struct
##

import os
import sys
import struct
import xml.etree.ElementTree as ET

DMARParserVersion = '1.01'


class DMAR_TABLE(object):
    # Header Lengths
    DMARHeaderLength = 48
    DRDHHeaderLength = 16
    RMRRHeaderLength = 24
    ASTRHeaderLength = 8
    ANDDHeaderLength = 8
    DeviceScopeHeaderLength = 6

    def __init__(self, data):
        self.dmar_table = self.ACPI_TABLE_HEADER(data)
        self.data = data[DMAR_TABLE.DMARHeaderLength:]
        while len(self.data) > 0:
            # Get type and length of remapping struct
            remapping_header = self.REMAPPING_STRUCT_HEADER(self.data)
            assert remapping_header.Type < 5, "Reserved remapping struct found in DMAR table"

            # Parse remapping struct
            if remapping_header.Type == 0:
                remapping_header = self.DRHD_STRUCT(self.data, remapping_header.Length)
            elif remapping_header.Type == 1:
                remapping_header = self.RMRR_STRUCT(self.data, remapping_header.Length)
                self.dmar_table.RMRRlist.append(remapping_header)
            elif remapping_header.Type == 2:
                remapping_header = self.ATSR_STRUCT(self.data, remapping_header.Length)
            elif remapping_header.Type == 3:
                remapping_header = self.RHSA_STRUCT(self.data, remapping_header.Length)
            elif remapping_header.Type == 4:
                remapping_header = self.ANDD_STRUCT(self.data, remapping_header.Length)
                self.dmar_table.ANDDCount += 1
            else:
                print('Reserved remapping struct found in DMAR table')
                sys.exit(-1)

            self.dmar_table.SubStructs.append(remapping_header)
            # Add to XML
            self.data = self.data[remapping_header.Length:]

        self.xml = self.toXml()

    def toXml(self):
        root = ET.Element('DMAR Table')
        root.append(self.dmar_table.toXml())
        for sub in self.dmar_table.SubStructs:
            root.append(sub.toXml())

        return root

    def __str__(self):
        retval = str(self.dmar_table)

        for sub in self.dmar_table.SubStructs:
            retval += str(sub)

        return retval

    def DMARBitEnabled(self):
        return bool(self.dmar_table.DMARBit)

    def ANDDCount(self):
        return self.dmar_table.ANDDCount

    def CheckRMRRCount(self, goldenxml=None):
        goldenignores = set()

        if goldenxml is None or not os.path.isfile(goldenxml):
            print("XML File not found")
        else:
            goldenfile = ET.parse(goldenxml)
            goldenroot = goldenfile.getroot()
            for RMRR in goldenroot:
                goldenignores.add(RMRR.find('Path').text.lower())

        for RMRR in self.dmar_table.RMRRlist:
            if RMRR.getPath() not in goldenignores:
                print("RMRR PCIe Endpoint " + RMRR.getPath() + " found but not in golden XML")
                return False

        return True

    class ACPI_TABLE_HEADER(object):
        struct_format = '=4sIBB6s8sI4sIBB'
        size = struct.calcsize(struct_format)

        def __init__(self, header_byte_array):
            (self.Signature,
             self.Length,
             self.Revision,
             self.Checksum,
             self.OEMID,
             self.OEMTableID,
             self.OEMRevision,
             self.CreatorID,
             self.CreatorRevision,
             self.HostAddressWidth,
             self.Flags) = struct.unpack_from(DMAR_TABLE.ACPI_TABLE_HEADER.struct_format, header_byte_array)

            self.DMARBit = self.Flags & 0x4
            self.ANDDCount = 0
            self.RMRRlist = list()
            self.SubStructs = list()

        def __str__(self):
            return """\n  ACPI Table Header
    ------------------------------------------------------------------
      Signature          : %s
      Length             : 0x%08X
      Revision           : 0x%02X
      Checksum           : 0x%02X
      OEM ID             : %s
      OEM Table ID       : %s
      OEM Revision       : 0x%08X
      Creator ID         : %s
      Creator Revision   : 0x%08X
      Host Address Width : 0x%02X
      Flags              : 0x%02X\n""" % (self.Signature, self.Length, self.Revision, self.Checksum,
                                          self.OEMID, self.OEMTableID, self.OEMRevision, self.CreatorID,
                                          self.CreatorRevision, self.HostAddressWidth, self.Flags)

        def toXml(self):
            xml_repr = ET.Element('AcpiTableHeader')
            xml_repr.set('Signature', '%s' % self.Signature)
            xml_repr.set('Length', '0x%X' % self.Length)
            xml_repr.set('Revision', '0x%X' % self.Revision)
            xml_repr.set('Checksum', '0x%X' % self.Checksum)
            xml_repr.set('OEMID', '%s' % self.OEMID)
            xml_repr.set('OEMTableID', '%s' % self.OEMTableID)
            xml_repr.set('OEMRevision', '0x%X' % self.OEMRevision)
            xml_repr.set('CreatorID', '%s' % self.CreatorID)
            xml_repr.set('CreatorRevision', '0x%X' % self.CreatorRevision)
            xml_repr.set('HostAddressWidth', '0x%X' % self.HostAddressWidth)
            xml_repr.set('Flags', '0x%X' % self.Flags)
            return xml_repr

    class REMAPPING_STRUCT_HEADER(object):
        struct_format = '=HH'

        def __init__(self, header_byte_array):
            (self.Type,
             self.Length) = struct.unpack_from(DMAR_TABLE.REMAPPING_STRUCT_HEADER.struct_format, header_byte_array)

        def __str__(self):
            return """\n  Remapping Struct Header
    ------------------------------------------------------------------
      Type               : 0x%04X
      Length             : 0x%04X
    """ % (self.Type, self.Length)

    class DRHD_STRUCT(REMAPPING_STRUCT_HEADER):
        struct_format = '=HHBBHQ'

        def __init__(self, header_byte_array, length):
            (self.Type,
             self.Length,
             self.Flags,
             self.Reserved,
             self.SegmentNumber,
             self.RegisterBaseAddress) = struct.unpack_from(DMAR_TABLE.DRHD_STRUCT.struct_format, header_byte_array)

            # Get Sub Structs
            self.DeviceScope = list()
            header_byte_array = header_byte_array[DMAR_TABLE.DRDHHeaderLength:]
            bytes_left = self.Length - DMAR_TABLE.DRDHHeaderLength
            while bytes_left > 0:
                device_scope = DMAR_TABLE.DEVICE_SCOPE_STRUCT(header_byte_array)
                header_byte_array = header_byte_array[device_scope.Length:]
                bytes_left -= device_scope.Length
                self.DeviceScope.append(device_scope)

        def toXml(self):
            xml_repr = ET.Element('DRHD')
            xml_repr.set('Type', '0x%X' % self.Type)
            xml_repr.set('Length', '0x%X' % self.Length)
            xml_repr.set('Flags', '0x%X' % self.Flags)
            xml_repr.set('Reserved', '0x%X' % self.Reserved)
            xml_repr.set('SegmentNumber', '0x%X' % self.SegmentNumber)
            xml_repr.set('RegisterBaseAddress', '0x%X' % self.RegisterBaseAddress)

            # Add SubStructs
            for item in self.DeviceScope:
                xml_subitem = ET.SubElement(xml_repr, item.TypeString)
                xml_subitem.set('Type', '0x%X' % item.Type)
                xml_subitem.set('Length', '0x%X' % item.Length)
                xml_subitem.set('Reserved', '0x%X' % item.Reserved)
                xml_subitem.set('EnumerationID', '0x%X' % item.EnumerationID)
                xml_subitem.set('StartBusNumber', '0x%X' % item.StartBusNumber)

            return xml_repr

        def __str__(self):
            retstring = """\n  DRHD
    ------------------------------------------------------------------
      Type                  : 0x%04X
      Length                : 0x%04X
      Flags                 : 0x%02X
      Reserved              : 0x%02X
      Segment Number        : 0x%04x
      Register Base Address : 0x%016x
    """ % (self.Type, self.Length, self.Flags, self.Reserved, self.SegmentNumber, self.RegisterBaseAddress)

            for item in self.DeviceScope:
                retstring += str(item)

            return retstring

    class RMRR_STRUCT(REMAPPING_STRUCT_HEADER):
        struct_format = '=HHHHQQ'

        def __init__(self, header_byte_array, length):
            (self.Type,
             self.Length,
             self.Reserved,
             self.SegmentNumber,
             self.ReservedMemoryBaseAddress,
             self.ReservedMemoryRegionLimitAddress) = struct.unpack_from(DMAR_TABLE.RMRR_STRUCT.struct_format,
                                                                         header_byte_array)

            # Get Sub Structs
            self.DeviceScope = list()
            header_byte_array = header_byte_array[DMAR_TABLE.RMRRHeaderLength:]
            bytes_left = self.Length - DMAR_TABLE.RMRRHeaderLength
            while bytes_left > 0:
                device_scope = DMAR_TABLE.DEVICE_SCOPE_STRUCT(header_byte_array)
                header_byte_array = header_byte_array[device_scope.Length:]
                bytes_left -= device_scope.Length
                self.DeviceScope.append(device_scope)

        def getPath(self):
            retString = ""
            for index, item in enumerate(self.DeviceScope):
                retString += self.DeviceScope[index].getPath()
                if index != len(self.DeviceScope) - 1:
                    retString += ", "
            return retString

        def toXml(self):
            xml_repr = ET.Element('RMRR')
            xml_repr.set('Type', '0x%X' % self.Type)
            xml_repr.set('Length', '0x%X' % self.Length)
            xml_repr.set('Reserved', '0x%X' % self.Reserved)
            xml_repr.set('SegmentNumber', '0x%X' % self.SegmentNumber)
            xml_repr.set('ReservedMemoryBaseAddress', '0x%X' % self.ReservedMemoryBaseAddress)
            xml_repr.set('ReservedMemoryRegionLimitAddress', '0x%X' % self.ReservedMemoryRegionLimitAddress)

            # Add SubStructs
            for item in self.DeviceScope:
                xml_subitem = ET.SubElement(xml_repr, item.TypeString)
                xml_subitem.set('Type', '0x%X' % item.Type)
                xml_subitem.set('Length', '0x%X' % item.Length)
                xml_subitem.set('Reserved', '0x%X' % item.Reserved)
                xml_subitem.set('EnumerationID', '0x%X' % item.EnumerationID)
                xml_subitem.set('StartBusNumber', '0x%X' % item.StartBusNumber)

            return xml_repr

        def __str__(self):
            retstring = """\n  RMRR
    ------------------------------------------------------------------
      Type                                 : 0x%04X
      Length                               : 0x%04X
      Reserved                             : 0x%04X
      Segment Number                       : 0x%04x
      Reserved Memory Base Address         : 0x%016x
      Reserved Memory Region Limit Address : 0x%016x\n""" % (self.Type, self.Length, self.Reserved,
                                                             self.SegmentNumber, self.ReservedMemoryBaseAddress,
                                                             self.ReservedMemoryRegionLimitAddress)

            for item in self.DeviceScope:
                retstring += str(item)

            return retstring

    class ATSR_STRUCT(REMAPPING_STRUCT_HEADER):
        struct_format = '=HHBBH'

        def __init__(self, header_byte_array, length):
            (self.Type,
             self.Length,
             self.Flags,
             self.Reserved,
             self.SegmentNumber) = struct.unpack_from(DMAR_TABLE.ATSR_STRUCT.struct_format, header_byte_array)

            # Get Sub Structs
            self.DeviceScope = list()
            header_byte_array = header_byte_array[DMAR_TABLE.ASTRHeaderLength:]
            bytes_left = self.Length - DMAR_TABLE.ASTRHeaderLength
            while bytes_left > 0:
                device_scope = DMAR_TABLE.DEVICE_SCOPE_STRUCT(header_byte_array)
                header_byte_array = header_byte_array[device_scope.Length:]
                bytes_left -= device_scope.Length
                self.DeviceScope.append(device_scope)

        def toXml(self):
            xml_repr = ET.Element('ASTR')
            xml_repr.set('Type', '0x%X' % self.Type)
            xml_repr.set('Length', '0x%X' % self.Length)
            xml_repr.set('Flags', '0x%X' % self.Flags)
            xml_repr.set('Reserved', '0x%X' % self.Reserved)
            xml_repr.set('SegmentNumber', '0x%X' % self.SegmentNumber)

            # Add SubStructs
            for item in self.DeviceScope:
                xml_subitem = ET.SubElement(xml_repr, item.TypeString)
                xml_subitem.set('Type', '0x%X' % item.Type)
                xml_subitem.set('Length', '0x%X' % item.Length)
                xml_subitem.set('Reserved', '0x%X' % item.Reserved)
                xml_subitem.set('EnumerationID', '0x%X' % item.EnumerationID)
                xml_subitem.set('StartBusNumber', '0x%X' % item.StartBusNumber)

            return xml_repr

        def __str__(self):
            retstring = """\n  ASTR
    ------------------------------------------------------------------
      Type                                 : 0x%04X
      Length                               : 0x%04X
      Flags                                : 0x%02X
      Reserved                             : 0x%02X
      Segment Number                       : 0x%04x
    """ % (self.Type, self.Length, self.Flags, self.Reserved, self.SegmentNumber)

            for item in self.DeviceScope:
                retstring += str(item)

            return retstring

    class RHSA_STRUCT(REMAPPING_STRUCT_HEADER):
        struct_format = '=HHIQI'

        def __init__(self, header_byte_array, length):
            (self.Type,
             self.Length,
             self.Reserved,
             self.RegisterBaseAddress,
             self.ProximityDomain) = struct.unpack_from(DMAR_TABLE.RHSA_STRUCT.struct_format, header_byte_array)

        def toXml(self):
            xml_repr = ET.Element('RHSA')
            xml_repr.set('Type', '0x%X' % self.Type)
            xml_repr.set('Length', '0x%X' % self.Length)
            xml_repr.set('Reserved', '0x%X' % self.Reserved)
            xml_repr.set('RegisterBaseAddress', '0x%X' % self.RegisterBaseAddress)
            xml_repr.set('ProximityDomain', '0x%X' % self.ProximityDomain)

            return xml_repr

        def __str__(self):
            return """\n  RHSA
    ------------------------------------------------------------------
      Type                                 : 0x%04X
      Length                               : 0x%04X
      Reserved                             : 0x%08X
      Register Base Address                : 0x%016X
      Proximity Domain                     : 0x%08x
    """ % (self.Type, self.Length, self.Reserved, self.RegisterBaseAddress, self.ProximityDomain)

    class ANDD_STRUCT(REMAPPING_STRUCT_HEADER):
        header_format = '=HH'

        def __init__(self, header_byte_array, length):
            self.struct_format = '=B'
            (self.Type,
             self.Length) = struct.unpack_from(DMAR_TABLE.ANDD_STRUCT.header_format, header_byte_array)

            # Since there is no variable of size 3 we need to manually pull into reserved
            self.Reserved = 0
            for i in range(6, 3, -1):
                self.Reserved = self.Reserved << 8
                self.Reserved |= struct.unpack("<B", header_byte_array[i:i + 1])[0]
            header_byte_array = header_byte_array[7:]

            # Unpack remaining values
            self.struct_format = self.struct_format + str(self.Length - DMAR_TABLE.ANDDHeaderLength) + 's'
            (self.ACPIDeviceNumber,
             self.ACPIObjectName) = struct.unpack_from(self.struct_format, header_byte_array)

        def toXml(self):
            xml_repr = ET.Element('ANDD')
            xml_repr.set('Type', '0x%X' % self.Type)
            xml_repr.set('Length', '0x%X' % self.Length)
            xml_repr.set('Reserved', '0x%X' % self.Reserved)
            xml_repr.set('ACPIDeviceNumber', '0x%X' % self.ACPIDeviceNumber)
            xml_repr.set('ACPIObjectName', '%s' % self.ACPIObjectName)

            return xml_repr

        def __str__(self):
            return """\n  ANDD
    ------------------------------------------------------------------
      Type                                 : 0x%04X
      Length                               : 0x%04X
      Reserved                             : 0x%06X
      ACPI Device Number                   : 0x%02X
      ACPI Object Name                     : %s
    """ % (self.Type, self.Length, self.Reserved, self.ACPIDeviceNumber, self.ACPIObjectName)

    class DEVICE_SCOPE_STRUCT(object):
        struct_format = '=BBHBB'

        def __init__(self, header_byte_array):
            (self.Type,
             self.Length,
             self.Reserved,
             self.EnumerationID,
             self.StartBusNumber) = struct.unpack_from(DMAR_TABLE.DEVICE_SCOPE_STRUCT.struct_format, header_byte_array)

            assert self.Type < 6, "Reserved Device Scope Type Found"

            if self.Type == 1:
                self.TypeString = "PCI Endpoint Device"
            elif self.Type == 2:
                self.TypeString = "PCI Sub-hierarchy"
            elif self.Type == 3:
                self.TypeString = "IOAPIC"
            elif self.Type == 4:
                self.TypeString = "MSI_CAPABLE_HPET"
            elif self.Type == 5:
                self.TypeString = "ACPI_NAMESPACE_DEVICE"
            else:
                print("Reserved Device Scope Type Found")
                sys.exit(-1)

            number_path_entries = (self.Length - DMAR_TABLE.DeviceScopeHeaderLength) / 2
            offset = 6
            self.Path = list()
            while number_path_entries > 0:
                self.Path.append((struct.unpack("<B", header_byte_array[offset:offset + 1]),
                                  struct.unpack("<B", header_byte_array[offset + 1:offset + 2])))
                offset += 2
                number_path_entries -= 1

        def getPath(self):
            retstring = "%02d" % self.StartBusNumber + ":"

            for (index, item) in enumerate(self.Path):
                retstring += "%02d" % item[0] + "." + "%01d" % item[1]
                if index != len(self.Path) - 1:
                    retstring += ":"

            return retstring

        def __str__(self):
            retstring = """\n\t\t  %s
    \t\t--------------------------------------------------
    \t\t  Type                  : 0x%02X
    \t\t  Length                : 0x%02X
    \t\t  Reserved              : 0x%04X
    \t\t  Enumeration ID        : 0x%02x
    \t\t  Start Bus Number      : 0x%02x
    \t\t  Path                  : """ % (self.TypeString, self.Type, self.Length, self.Reserved,
                                         self.EnumerationID, self.StartBusNumber)

            retstring += "%02d" % self.StartBusNumber + ":"
            for (index, item) in enumerate(self.Path):
                retstring += "%02d" % item[0] + "." + "%01d" % item[1]
                if index != len(self.Path) - 1:
                    retstring += ":"
            retstring += "\n"

            return retstring
