import logging
import struct

from ruamel.yaml import YAML

from util.common import common_getattr


# class FatException(Exception):
#     pass




#
# class FAT_Boot(object):
#     '''
#     Initializes fat boot sector.
#
#     :param offset: Offset on disk
#     :type offset: int
#     '''
#     layout = {
#         0x00: ('chJumpInstruction', '3s'),
#         0x03: ('chOemId', '8s'),
#         0x0B: ('wBytesPerSector', '<H'),
#         0x0D: ('uchSectorsPerCluster', 'B'),
#         0x0E: ('wSectorsCount', '<H'),  # reserved sectors (min 32?)
#         0x10: ('uchFATCopies', 'B'),
#         0x11: ('wMaxRootEntries', '<H'),
#         0x13: ('wTotalSectors', '<H'),
#         0x15: ('uchMediaDescriptor', 'B'),
#         0x16: ('wSectorsPerFAT', '<H'),  # not used, see 24h instead
#         0x18: ('wSectorsPerTrack', '<H'),
#         0x1A: ('wHeads', '<H'),
#         0x1C: ('wHiddenSectors', '<H'),
#         #0x1E: ('wTotalHiddenSectors', '<H'),
#         0x20: ('dwTotalLogicalSectors', '<I'),
#     }
#
#     def __init__(self, s=None, offset = 0):
#         self._i = 0
#         self._pos = offset #base offset of bootsector
#         self._buf = s or bytearray(512)
#         self._kv = self.layout.copy()
#         self._vk = {}  # { name: offset}
#         for k, v in self._kv.items():
#             self._vk[v[0]] = k
#             getattr(self, v[0])
#
#
#     def initBoot(self, size,
#                  chJumpInstruction = '\xEB\x58\x90',
#                  chOemId = 'Test',
#                  wBytesPerSector = 512,
#                  uchSectorsPerCluster = 32,
#                  wRsvdSectorsCount = 1,
#                  uchFatCopies = 2,
#                  wMaxRootEntries = 0,
#                  wTotalSectors = 0,
#                  uchMediaDescriptor = 0xF8,
#                  wSectorsPerFat = 0,
#                  wSectorsPerTrack = 63,
#                  wHeads = 16,
#                  wHiddenSectors = 0,
#                  dwTotalLogicalSectors = 0):
#         '''
#         Sets boot sector parameters.
#
#         :param size: disk size in bytes
#         :type size: int
#         :param chJumpInstruction: Jump instruction code
#         :type chJumpInstruction: Hex-String
#         :param chOemId: OEM Name
#         :type chOemId: String
#         :param wBytesPerSector: Bytes per sector (default: 512)
#         :type wBytesPerSector: int
#         :param uchSectorsPerCluster: sectors per cluster
#         :type uchSectorsPerCluster: int
#         :param wRsvdSectorsCount: Size in sectors of reserved area
#         :type wRsvdSectorsCount: int
#         :param uchFatCopies: Number of FATs. Typically two
#         :type uchFatCopies: int
#         :param wMaxRootEntries: Maximum number of files in root directory, for FAT12 and FAT16 only. Has to be 0 for FAT32
#         :type wMaxRootEntries: int
#         :param wTotalSectors: 16-bit value of number of sectors in file system
#         :type wTotalSectors: int
#         :param uchMediaDescriptor: Media type. Typically 0xf8 for fixed disks and 0xf0 for removable disk.
#         :type uchMediaDescriptor: Hex-Value
#         :param wSectorsPerFat: 16-bit size in sectors of each FAT for FAT12 and FAT16. 0 for FAT32
#         :type wSectorsPerFat: int
#         :param wSectorsPerTrack: Sectors per track of storage device
#         :type wSectorsPerTrack: int
#         :param wHeads: Number of heads in storage device
#         :type wHeads: int
#         :param wHiddenSectors: Number of sectors before the start of partition
#         :type wHiddenSectors: int
#         :param dwTotalLogicalSectors: 32-bit value of number of sectors in file system
#         :type dwTotalLogicalSectors:
#         :return: None
#         :rtype: None
#         '''
#         self.chJumpInstruction = chJumpInstruction
#         self.chOemId = b'%-8s' % str.encode(chOemId)
#         self.wBytesPerSector = wBytesPerSector
#
#         # Check valid uchSectorsPerCluster
#         # TODO: BytesPerCluster not greater than 32k (32 * 1024)
#         if uchSectorsPerCluster not in (1,2,4,8,16,32,64,128):
#             logging.warn("Sectors per cluster " + uchSectorsPerCluster + " not valid.")
#             #self.uchSectorsPerCluster = 32
#
#         self.uchSectorsPerCluster = uchSectorsPerCluster
#
#         self.uchSectorsPerCluster = uchSectorsPerCluster
#         self.wSectorsCount = wRsvdSectorsCount
#         self.uchFATCopies = uchFatCopies
#         self.wMaxRootEntries = wMaxRootEntries
#         self.wTotalSectors = wTotalSectors
#
#         # TODO: validate Media descriptor
#         self.uchMediaDescriptor = uchMediaDescriptor
#         self.wSectorsPerFAT = wSectorsPerFat
#         self.wSectorsPerTrack = wSectorsPerTrack
#         self.wHeads = wHeads
#         self.wHiddenSectors = wHiddenSectors
#         self.dwTotalLogicalSectors = dwTotalLogicalSectors
#
#
#     __getattr__ = common_getattr
#
#     def pack(self):
#         '''
#         Packs attributes to struct. Mapping of sizes is done with layout dictionary.
#
#         :return: Buffer object with mapped attributes
#         :rtype: Bytearray
#         '''
#
#         for k, v in self._kv.items():
#             logging.debug("Packing Fat boot sector parameters: " + v[0])
#             self._buf[k:k+struct.calcsize(v[1])] = struct.pack(v[1], getattr(self, v[0]))
#             logging.debug("Value of parameter: " + str(self._buf[k:k+struct.calcsize(v[1])]))
#         # TODO: init2 in fat
#         #self.__init2__()
#         return self._buf