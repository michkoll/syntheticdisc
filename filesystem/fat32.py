import logging
import struct

from filesystem.fat import FAT_Boot, FAT, FatException
from util.common import common_getattr

from util.fat32yaml import fat32Yaml


class FAT32(FAT):
    def __init__(self, stream = None):
        super().__init__("fat32", stream)

        self.boot = FAT32_Boot()
        self.fsinfo = FAT32FSINFO()


    def writeNew(self):
        if not self.stream:
            raise FatException("No stream given for writing!")
        else:
            self.stream.seek(0)

            self.stream.write(self.boot.pack())
            self.stream.write(self.fsinfo.pack())
            if self.boot.wBootCopySector:
                self.stream.seek(self.boot.wBootCopySector * self.boot.wBytesPerSector)
                self.stream.write(self.boot.pack())
                self.stream.write(self.fsinfo.pack())

        # Create blank FAT areas
        self.stream.seek(self.boot.fat())
        blank = bytearray(self.boot.wBytesPerSector)
        for i in range(self.boot.dwSectorsPerFAT * 2):
            self.stream.write(blank)

        # Initialize FAT1
        clus_0_2 = b'\xF8\xFF\xFF\x0F\xFF\xFF\xFF\xFF\xF8\xFF\xFF\x0F'
        self.stream.seek(self.boot.wSectorsCount * self.boot.wBytesPerSector)
        self.stream.write(clus_0_2)

        # ... and FAT2
        if self.boot.uchFATCopies == 2:
            self.stream.seek(self.boot.fat(1))
            self.stream.write(bytearray(self.boot.cluster))

        # Blank root directory
        self.stream.seek(self.boot.root())
        self.stream.write(bytearray(self.boot.cluster))

        sizes = {0:'B', 10:'KiB',20:'MiB',30:'GiB',40:'TiB',50:'EiB'}
        k = 0
        for k in sorted(sizes):
            if (self.boot.fsinfo['required_size'] / (1<<k)) < 1024: break

        free_clusters = self.boot.fsinfo['clusters'] - 1
        print("Successfully applied FAT32 to a %.02f %s volume.\n%d clusters of %.1f KB.\n%.02f %s free in %d clusters." % (self.boot.fsinfo['required_size']/float(1<<k), sizes[k], self.boot.fsinfo['clusters'], self.boot.fsinfo['cluster_size']/1024.0, free_clusters*self.boot.cluster/float(1<<k), sizes[k], free_clusters))
        print("\nFAT #1 @0x%X, Data Region @0x%X, Root (cluster #%d) @0x%X" % (self.boot.fatoffs, self.boot.cl2offset(2), 2, self.boot.cl2offset(2)))

        return 0



class FAT32_Boot(FAT_Boot):
    layout = dict(FAT_Boot.layout)
    layout.update({
        0x24: ('dwSectorsPerFAT', '<I'),
        0x28: ('wMirroringFlags', '<H'),  # bits 0-3: active FAT, it bit 7 set; else: mirroring as usual
        0x2A: ('wVersion', '<H'),
        0x2C: ('dwRootCluster', '<I'),  # usually 2
        0x30: ('wFSISector', '<H'),  # usually 1
        0x32: ('wBootCopySector', '<H'),  # 0x0000 or 0xFFFF if unused, usually 6
        0x34: ('chReserved', '12s'),
        0x40: ('chPhysDriveNumber', 'B'),
        0x41: ('chReserved1', 'B'),
        0x42: ('chExtBootSignature', 'B'),
        0x43: ('dwVolumeID', '<I'),
        0x47: ('sVolumeLabel', '11s'),
        0x52: ('sFSType', '8s'),
        # ~ 0x72: ('chBootstrapCode', '390s'),
        0x1FE: ('wBootSignature', '<H')  # 55 AA
    })

    def __init__(self, offset = 0):
        logging.debug("Init FAT32 Bootcode")
        super().__init__(offset=offset)


    def __init2__(self):
        if not hasattr(self, 'wBytesPerSector'): return

        # Cluster size in bytes
        self.cluster = self.wBytesPerSector * self.uchSectorsPerCluster

        # Offset of first FAT copy
        self.fatoffs = self.wSectorsCount * self.wBytesPerSector + self._pos

        # Data area offset
        self.dataoffs = self.fatoffs + self.uchFATCopies * self.dwSectorsPerFAT * self.wBytesPerSector + self._pos

        # Number of cluster represented in this FAT
        self.fatsize = self.dwTotalLogicalSectors/self.uchSectorsPerCluster

    def initBootFromConfig(self, size, fat32BootConfig):
        self.initBoot(size, **fat32BootConfig)

    def initBoot(self, size,
                 chJumpInstruction = b'\xEB\x58\x90',
                 chOemId = 'Test',
                 wBytesPerSector = 512,
                 uchSectorsPerCluster = 32,
                 wRsvdSectorsCount = 32,
                 uchFatCopies = 2,
                 wMaxRootEntries=0,
                 wTotalSectors=0,
                 uchMediaDescriptor=0xF8,
                 wSectorsPerFat=0,
                 wSectorsPerTrack=63,
                 wHeads=16,
                 wHiddenSectors=0,
                 dwSectorsPerFat = 0,
                 dwRootCluster = 2,
                 wFSISector = 1,
                 wBootCopySector = 6,
                 chReserved = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
                 chPhysDriveNumber = 0x80,
                 chReserved1 = 0x00,
                 chExtBootSignature = 0x29,
                 wBootSignature = 0xAA55,
                 dwVolumeID = 1234567890,
                 sVolumeLabel = 'TEST',
                 sFSType = 'FAT32'
                 ):
        sectors = int(size / wBytesPerSector)

        if (sectors > 0xFFFFFF):
            logging.critical("Too many sectors for FAT32 file system. Please lower size or higher sector size.")
            raise FatException("Too many sectors for FAT32 file system. Please lower size or higher sector size.")

        super().initBoot(size, chJumpInstruction, chOemId, wBytesPerSector, uchSectorsPerCluster, wRsvdSectorsCount,
                         uchFatCopies, wMaxRootEntries, wTotalSectors, uchMediaDescriptor, wSectorsPerFat, wSectorsPerTrack, wHeads, wHiddenSectors, sectors)

        reserved_size = wRsvdSectorsCount * wBytesPerSector
        allowed = {}  # {cluster_size : fsinfo}

        for i in range(9, 17):  # cluster sizes 0.5K...64K
            self.fsinfo = {}
            cluster_size = (2 ** i)
            clusters = (size - reserved_size) / cluster_size
            fat_size = rdiv(4 * (clusters + 2), wBytesPerSector) * wBytesPerSector
            required_size = cluster_size * clusters + uchFatCopies * fat_size + reserved_size
            while required_size > size:
                clusters -= 1
                fat_size = rdiv(4 * (clusters + 2), wBytesPerSector) * wBytesPerSector
                required_size = cluster_size * clusters + uchFatCopies * fat_size + reserved_size
            if (clusters < 65526 ) or clusters > 0x0FFFFFF6:  # MS imposed limits
                continue
            self.fsinfo['required_size'] = int(required_size)  # space occupied by FS
            self.fsinfo['reserved_size'] = reserved_size  # space reserved before FAT#1
            self.fsinfo['cluster_size'] = cluster_size
            self.fsinfo['clusters'] = int(clusters)
            self.fsinfo['fat_size'] = int(fat_size)  # space occupied by a FAT copy
            allowed[cluster_size] = self.fsinfo

        # TODO: Which sector per Fat to choose?
        self.fsinfo = allowed[wBytesPerSector * uchSectorsPerCluster]
        self._clusters = self.fsinfo['clusters']
        # calculated, if parameter is not 0 than value ist set without validation
        if dwSectorsPerFat != 0:
            self.dwSectorsPerFAT = dwSectorsPerFat
        else:
            self.dwSectorsPerFAT = int(self.fsinfo['fat_size']/wBytesPerSector)

        # TODO: wMirroringFlags
        self.wMirroringFlags = 0
        # TODO: wVersion
        self.wVersion = 0

        self.dwRootCluster = dwRootCluster
        self.wFSISector = wFSISector
        self.wBootCopySector = wBootCopySector

        # TODO: chReserved filling
        #self.chReserved = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self.chReserved = chReserved

        self.chPhysDriveNumber = chPhysDriveNumber

        # TODO: chFlags
        self.chReserved1 = chReserved1

        self.chExtBootSignature = chExtBootSignature
        self.wBootSignature = wBootSignature
        self.dwVolumeID = dwVolumeID
        self.sVolumeLabel = b'%-11s' % str.encode(sVolumeLabel)
        self.sFSType = b'%-8s' % b'FAT32'

        self.__init2__()

    def fat(self, fatcopy=0):
        '''
        Returns position of given fatcopy in bytes
        :param fatcopy: Number of fatcopy (0: default, 1: first copy)
        :return: Position of FAT in bytes
        '''
        return self.fatoffs + fatcopy * self.dwSectorsPerFAT * self.wBytesPerSector

    def root(self):
        '''
        Returns the real offset of the root directory

        :return: Offset of root directory
        '''
        return self.cl2offset(self.dwRootCluster)

    def cl2offset(self, cluster):
        '''
        Returns the real offset of a cluster from disk start

        :param cluster: Number of cluster
        :return: Offset of cluster
        '''
        return self.dataoffs + (cluster - 2) * self.cluster

class FAT32BootParameter(fat32Yaml):
    yaml_tag = u'!Fat32BootParameter'
    def __init__(self, chJumpInstruction,
                 chOemId,
                 wBytesPerSector,
                 uchSectorsPerCluster,
                 wRsvdSectorsCount,
                 uchFatCopies,
                 wMaxRootEntries,
                 wTotalSectors,
                 uchMediaDescriptor,
                 wSectorsPerFat,
                 wSectorsPerTrack,
                 wHeads,
                 wHiddenSectors,
                 dwSectorsPerFat,
                 dwRootCluster,
                 wFSISector,
                 wBootCopySector,
                 chReserved,
                 chPhysDriveNumber,
                 chReserved1,
                 chExtBootSignature,
                 wBootSignature,
                 dwVolumeID,
                 sVolumeLabel,
                 sFSType):
        self.chJumpInstruction = chJumpInstruction
        self.chOemId = chOemId
        self.wBytesPerSector = wBytesPerSector
        self.uchSectorsPerCluster = uchSectorsPerCluster
        self.wRsvdSectorsCount = wRsvdSectorsCount
        self.uchFatCopies = uchFatCopies
        self.wMaxRootEntries = wMaxRootEntries
        self.wTotalSectors = wTotalSectors
        self.uchMediaDescriptor = uchMediaDescriptor
        self.wSectorsPerFat = wSectorsPerFat
        self.wSectorsPerTrack = wSectorsPerTrack
        self.wHeads = wHeads
        self.wHiddenSectors = wHiddenSectors
        self.dwSectorsPerFat = dwSectorsPerFat
        self.dwRootCluster = dwRootCluster
        self.wFSISector = wFSISector
        self.wBootCopySector = wBootCopySector
        self.chReserved = chReserved
        self.chPhysDriveNumber = chPhysDriveNumber
        self.chReserved1 = chReserved1
        self.chExtBootSignature = chExtBootSignature
        self.wBootSignature = wBootSignature
        self.dwVolumeID = dwVolumeID
        self.sVolumeLabel = sVolumeLabel
        self.sFSType = sFSType
        pass



class FAT32FSINFO(object):
    layout = {  # { offset: (name, unpack string) }
        0x00: ('sSignature1', '4s'),  # RRaA
        0x04: ('sReserved1', '480s'),
        0x1E4: ('sSignature2', '4s'),  # rrAa
        0x1E8: ('dwFreeClusters', '<I'),  # 0xFFFFFFFF if unused (may be incorrect)
        0x1EC: ('dwNextFreeCluster', '<I'),  # hint only (0xFFFFFFFF if unused)
        0x1F0: ('sReserved2', '12s'),
        0x1FE: ('wBootSignature', '<H')  # 55 AA
    }  # Size = 0x200 (512 byte)

    def __init__(self, offset = 0):
        logging.debug("Init FAT32 FSINFO")
        self._kv = self.layout.copy()
        self._buf = bytearray(512)  # normal FSInfo sector size
        pass

    __getattr__ = common_getattr

    def pack(self):
        "Update internal buffer"
        for k, v in self._kv.items():
            logging.debug("Packing Fat boot sector parameters: " + v[0])
            self._buf[k:k+struct.calcsize(v[1])] = struct.pack(v[1], getattr(self, v[0]))
        return self._buf

    def initFsInfoFromConfig(self, offset, fsInfoConfig):
        self.initFSInfo(offset=0, **fsInfoConfig)

    def initFSInfo(self, offset = 0, sSignature1 ='RRaA', sReserved1 = '', sSignature2 ='rrAa', dwFreeClusters = 0, dwNextFreeCluster = 3, sReserved2 = '', wBootSignature = 0xAA55):
        self._pos = offset
        self.sSignature1 = str.encode(sSignature1)
        self.sSignature2 = str.encode(sSignature2)

        # Transform sReserved1 to Bytearray, length 480
        reserved1 = bytearray(480)
        reserved1[0:0] = str.encode(sReserved1)
        self.sReserved1 = reserved1
        self.dwFreeClusters = dwFreeClusters
        self.dwNextFreeCluster = dwNextFreeCluster
        reserved2 = bytearray(12)
        reserved2[0:0] = str.encode(sReserved2)
        self.sReserved2 = reserved2
        self.wBootSignature = wBootSignature

class FAT32FsInfoParameter(fat32Yaml):
    yaml_tag = u'!FAT32FsInfoParameter'

    def __init__(self,
                 sSignature1,
                 sSignature2,
                 sReserved1,
                 dwFreeClusters,
                 dwNextFreeCluster,
                 sReserved2,
                 wBootSignature):
        self.sSignature1 = sSignature1
        self.sSignature2 = sSignature2
        self.sReserved1 = sReserved1
        self.dwFreeClusters = dwFreeClusters
        self.dwNextFreeCluster = dwNextFreeCluster
        self.sReserved2 = sReserved2
        self.wBootSignature = wBootSignature
        pass

class FAT32Parameter(fat32Yaml):
    yaml_tag = u'!FAT32Parameter'

    def __init__(self, fat32bootparameter, fat32fsinfoparameter):
        self.boot = fat32bootparameter
        self.fsinfo = fat32fsinfoparameter

def rdiv(a, b):
    "Divide a by b eventually rounding up"
    if a % b:
        return a / b + 1
    else:
        return a / b