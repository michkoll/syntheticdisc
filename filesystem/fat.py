import logging
import struct

from ruamel.yaml import YAML

from util.common import common_getattr


class FatException(Exception):
    pass


class FAT(object):

    def __init__(self, fstype = "fat32", stream = None):
        self.fstype = fstype
        self.stream = stream




class FAT_Boot(YAML):
    layout = {
        0x00: ('chJumpInstruction', '<L'),
        0x03: ('chOemId', '8s'),
        0x0B: ('wBytesPerSector', '<H'),
        0x0D: ('uchSectorsPerCluster', 'B'),
        0x0E: ('wSectorsCount', '<H'),  # reserved sectors (min 32?)
        0x10: ('uchFATCopies', 'B'),
        0x11: ('wMaxRootEntries', '<H'),
        0x13: ('wTotalSectors', '<H'),
        0x15: ('uchMediaDescriptor', 'B'),
        0x16: ('wSectorsPerFAT', '<H'),  # not used, see 24h instead
        0x18: ('wSectorsPerTrack', '<H'),
        0x1A: ('wHeads', '<H'),
        0x1C: ('wHiddenSectors', '<H'),
        #0x1E: ('wTotalHiddenSectors', '<H'),
        0x20: ('dwTotalLogicalSectors', '<I'),
    }

    def __init__(self, offset = 0):
        self._kv = self.layout.copy()
        self._pos = offset #base offset of bootsector
        self._buf = bytearray(512)
        self._vk = {}  # { name: offset}
        for k, v in self._kv.items():
            self._vk[v[0]] = k
        pass

    def initBoot(self, size,
                 chJumpInstruction = '\xEB\x58\x90',
                 chOemId = 'Test',
                 wBytesPerSector = 512,
                 uchSectorsPerCluster = 32,
                 wRsvdSectorsCount = 1,
                 uchFatCopies = 2,
                 wMaxRootEntries = 0,
                 wTotalSectors = 0,
                 uchMediaDescriptor = 0xF8,
                 wSectorsPerFat = 0,
                 wSectorsPerTrack = 63,
                 wHeads = 16,
                 wHiddenSectors = 0,
                 dwTotalLogicalSectors = 0):
        self.chJumpInstruction = chJumpInstruction
        self.chOemId = b'%-8s' % str.encode(chOemId)
        self.wBytesPerSector = wBytesPerSector

        # Check valid uchSectorsPerCluster
        # TODO: BytesPerCluster not greater than 32k (32 * 1024)
        if uchSectorsPerCluster not in (1,2,4,8,16,32,64,128):
            logging.warn("Sectors per cluster " + uchSectorsPerCluster + " not valid. Correcting to 32")
            self.uchSectorsPerCluster = 32
        else:
            self.uchSectorsPerCluster = uchSectorsPerCluster

        self.uchSectorsPerCluster = uchSectorsPerCluster
        self.wSectorsCount = wRsvdSectorsCount
        self.uchFATCopies = uchFatCopies
        self.wMaxRootEntries = wMaxRootEntries
        self.wTotalSectors = wTotalSectors

        # TODO: validate Media descriptor
        self.uchMediaDescriptor = uchMediaDescriptor
        self.wSectorsPerFAT = wSectorsPerFat
        self.wSectorsPerTrack = wSectorsPerTrack
        self.wHeads = wHeads
        self.wHiddenSectors = wHiddenSectors
        self.dwTotalLogicalSectors = dwTotalLogicalSectors

        pass

    #__getattr__ = common_getattr

    def pack(self):

        for k, v in self._kv.items():
            logging.debug("Packing Fat boot sector parameters: " + v[0])
            self._buf[k:k+struct.calcsize(v[1])] = struct.pack(v[1], getattr(self, v[0]))
            logging.debug("Value of parameter: " + str(self._buf[k:k+struct.calcsize(v[1])]))
        # TODO: init2 in fat
        #self.__init2__()
        return self._buf
        pass