import argparse

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

def createFat(fatConfigFile, diskPath):
    # register classes for serialization
    yaml = ruamel.yaml.YAML()
    yaml.register_class(FAT32BootParameter)
    yaml.register_class(FAT32FsInfoParameter)
    yaml.register_class(FAT32Parameter)

    # deserialize fat config file
    with open('yaml/fat32.yml', 'r') as inpFat32:
        params = yaml.load(inpFat32)

    # create disk object and read first sector
    disk = Disk("../tests/images/Testimage.img", 'r+b', 0)
    s = disk.read(512)

    # create fat boot and fsi object
    boot, fsi = FATCreator.mkfat32FromConfig(stream=disk, size=disk.size, fat32bootSectorConfig=vars(params.boot), fsInfoConfig=vars(params.fsinfo))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create fat from config")
    parser.add_argument("fatConfig", help="filename of fat yaml config")
    parser.add_argument("diskPath", help="path to image file")
    args = parser.parse_args()

    createFat(fatConfigFile=args.fatConfig, diskPath=args.diskPath)