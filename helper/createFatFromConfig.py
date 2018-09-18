
import ruamel.yaml

from disktools.disk import Disk
import logging

from filesystem.fat32 import FAT32, FAT32_Boot, FATCreator, FAT, Dirtable
from model.fat32model import *

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

disk = Disk("../tests/images/Testimage.img", 'r+b', 0)
s = disk.read(512)
#fat = FAT32(s=s, stream=disk)
#fat = FATtest(s=s, stream=disk)
#fat.boot.mkfatFromConfig(disk.size, vars(params.boot))
#fat.fsinfo.initFsInfoFromConfig(offset=0, fsInfoConfig=vars(params.fsinfo))
#fat.boot.initBoot(disk.size, chOemId='next', sVolumeLabel='Blubb')
#fat.fsinfo.initFSInfo(offset=fat.boot.wBytesPerSector, dwFreeClusters=fat.boot._clusters - 1, dwNextFreeCluster=3)

boot, fsi = FATCreator.mkfat32FromConfig(stream=disk, size=disk.size, fat32bootSectorConfig=vars(params.boot), fsInfoConfig=vars(params.fsinfo))

fat = FAT(disk, boot.fatoffs, boot.clusters(), 32)

dt = Dirtable(boot, fat, boot.dwRootCluster)
dt.mkdir('SHORT')
dt.mkdir("Long")
subdir = dt.opendir('Long')

ch = subdir.mkdir("Child")

f1 = ch.create('Datei1.txt')
f1.File.write(b'Das ist der Inhalt der Datei1')
f1.close()

f2 = ch.create('LangeDatei.txt')
f2.File.write(boot.cluster * b'A' + boot.cluster * b'a' + boot.cluster * b'A')

ch2 = subdir.mkdir('Child2')




pass
