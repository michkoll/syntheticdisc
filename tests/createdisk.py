import struct
import sys
import ruamel.yaml

from disktools.disk import Disk
import logging

from filesystem.fat import FAT, FAT_Boot
from filesystem.fat32 import FAT32, FAT32_Boot

logPath = "./"
fileName = "Disk"
logging.basicConfig(level=logging.DEBUG,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format(logPath, fileName)),
        logging.StreamHandler()
    ])

#print(struct.unpack('4s',b'\x18\x06\x00\x00'))

disk = Disk("images/Testimage.img", 'r+b', 0)
fat = FAT32(disk)
fat.boot.initBoot(disk.size, chOemId='next', sVolumeLabel='Blubb')
fat.fsinfo.initFSInfo(offset=fat.boot.wBytesPerSector, dwFreeClusters=fat.boot._clusters - 1, dwNextFreeCluster=3)
#disk.seek(0)
#disk.write(fat.boot.pack())
#disk.write(fat.fsinfo.pack())
fat.writeNew()


print(disk)