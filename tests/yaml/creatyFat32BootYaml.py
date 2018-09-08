import ruamel.yaml
import logging

from filesystem.fat32 import FAT32BootParameter, FAT32FsInfoParameter, FAT32Parameter

logPath = "./"
fileName = "Disk"
logging.basicConfig(level=logging.DEBUG,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format(logPath, fileName)),
        logging.StreamHandler()
    ])

yaml = ruamel.yaml.YAML()

yaml.register_class(FAT32BootParameter)
yaml.register_class(FAT32FsInfoParameter)
yaml.register_class(FAT32Parameter)

bootparam = FAT32BootParameter(chJumpInstruction = 0x9058EB,
                 chOemId = 'Test',
                 wBytesPerSector = 512,
                 uchSectorsPerCluster = 32,
                 wRsvdSectorsCount = 32,
                 uchFatCopies = 2,
                  wMaxRootEntries = 0,
                 wTotalSectors = 0,
                 uchMediaDescriptor=0xF8,
                  wSectorsPerFat = 0,
                 wSectorsPerTrack = 63,
                 wHeads = 16,
                 wHiddenSectors=0,
                 dwSectorsPerFat = 0,
                 dwRootCluster = 2,
                 wFSISector = 1,
                 wBootCopySector = 6,
                 chReserved=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
                 chPhysDriveNumber = 0x80,
                 chReserved1=0x00,
                 chExtBootSignature = 0x29,
                 wBootSignature = 0xAA55,
                 dwVolumeID = 1234567890,
                 sVolumeLabel = 'TEST',
                 sFSType = 'FAT32')

fsinfo = FAT32FsInfoParameter(sSignature1 ='RRaA',
                              sReserved1 = '',
                              sSignature2 ='rrAa',
                              dwFreeClusters = 0,
                              dwNextFreeCluster = 3,
                              sReserved2 = '',
                              wBootSignature = 0xAA55)

fat32 = FAT32Parameter(bootparam, fsinfo)

with open('fat32boot.yml', 'w') as outfile:
    yaml.dump(bootparam, outfile)

with open('fat32fsi.yml', 'w') as outfileFSI:
    yaml.dump(fsinfo, outfileFSI)

with open('fat32.yml', 'w') as outfileParam:
    yaml.dump(fat32, outfileParam)