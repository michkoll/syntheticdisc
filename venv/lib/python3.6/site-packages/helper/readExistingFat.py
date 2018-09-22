import argparse

from disktools.disk import Disk
import logging

from filesystem.fat32 import FAT32, FAT32_Boot
from model.fat32model import *

# log configuration
loglevel = logging.INFO
logPath = "./"
fileName = "Disk"
logging.basicConfig(level=loglevel,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format(logPath, fileName)),
        logging.StreamHandler()
    ])

def main(diskPath):
    # Create instance of Disk object for further reading and writing access to image file
    # The image file has to be created before
    disk = Disk(diskPath, 'r+b', 0)

    # Reads boot sector in bytearray
    s = disk.read(512)

    # Creates fat object from given stream
    fat = FAT32(s=s, stream=disk)

    print(fat.boot)
    print(fat.fsinfo)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read image file and print fat parameters to stdout")
    parser.add_argument("diskPath", help="path to image file", type=int)
    args = parser.parse_args()

    main(diskPath=args.diskPath)