from util.commonYaml import fat32Yaml


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