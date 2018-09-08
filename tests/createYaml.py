from filesystem.fat32 import FAT32_Boot, FAT32BootParameter, FAT32FsInfoParameter, FAT32Parameter
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

yaml = ruamel.yaml.YAML()

yaml.register_class(FAT32BootParameter)
yaml.register_class(FAT32FsInfoParameter)
yaml.register_class(FAT32Parameter)



with open('yaml/fat32boot.yml', 'r') as inpfile:
    newboot = yaml.load(inpfile)

with open('yaml/fat32fsi.yml', 'r') as inpfileFSI:
    fsinfo = yaml.load(inpfileFSI)

with open('yaml/fat32.yml', 'r') as inpFat32:
    params = yaml.load(inpFat32)

disk = Disk("images/Testimage.img", 'r+b', 0)
fat = FAT32(disk)
fat.boot.initBootFromConfig(disk.size, vars(params.boot))
fat.fsinfo.initFsInfoFromConfig(offset=0, fsInfoConfig=vars(params.fsinfo))
#fat.boot.initBoot(disk.size, chOemId='next', sVolumeLabel='Blubb')
#fat.fsinfo.initFSInfo(offset=fat.boot.wBytesPerSector, dwFreeClusters=fat.boot._clusters - 1, dwNextFreeCluster=3)

fat.writeNew()


pass
