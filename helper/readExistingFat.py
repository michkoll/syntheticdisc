from disktools.disk import Disk
import logging

from filesystem.fat32 import FAT32, FAT32_Boot
from model.fat32model import *

logPath = "./"
fileName = "Disk"
logging.basicConfig(level=logging.DEBUG,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format(logPath, fileName)),
        logging.StreamHandler()
    ])

disk = Disk('../tests/images/Testimage.img','r+b')
s = disk.read(512)
fat = FAT32(s=s, stream=disk)
print(fat)