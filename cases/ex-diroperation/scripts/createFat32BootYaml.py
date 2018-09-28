import os

import ruamel.yaml
import logging

from model.fat32model import *

logPath = "./"
fileName = "Disk"
logging.basicConfig(level=logging.DEBUG,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format(logPath, fileName)),
        logging.StreamHandler()
    ])

def createBootYaml(destPath):
    yaml = ruamel.yaml.YAML()

    yaml.register_class(FAT32BootParameter)
    yaml.register_class(FAT32FsInfoParameter)
    yaml.register_class(FAT32Parameter)

    bootparam = FAT32BootParameter(chJumpInstruction = b'\xEB\x58\x90',
                     chOemId = 'EX-DIROP',
                     wBytesPerSector = 512,
                     uchSectorsPerCluster = 2,
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
                     sVolumeLabel = 'M111',
                     sFSType = 'FAT32')

    fsinfo = FAT32FsInfoParameter(sSignature1 ='RRaA',
                                  sReserved1 = '',
                                  sSignature2 ='rrAa',
                                  dwFreeClusters = 0,
                                  dwNextFreeCluster = 3,
                                  sReserved2 = '',
                                  wBootSignature = 0xAA55)

    fat32 = FAT32Parameter(bootparam, fsinfo)

    with open(os.path.join(destPath, 'fat32boot.yml'), 'w') as outfile:
        yaml.dump(bootparam, outfile)

    with open(os.path.join(destPath, 'fsinfo.yml'), 'w') as outfileFSI:
        yaml.dump(fsinfo, outfileFSI)

    with open(os.path.join(destPath, 'fat32.yml'), 'w') as outfileParam:
        yaml.dump(fat32, outfileParam)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create workflow and save to yaml file")
    parser.add_argument("destPath", help="destination path for boot config")
    args = parser.parse_args()

    createBootYaml(yamlPath=args.destPath)
