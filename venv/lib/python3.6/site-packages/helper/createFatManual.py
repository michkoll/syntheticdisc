from disktools.disk import Disk
import logging

from filesystem.fat32 import FATCreator

# log configuration
loglevel = logging.DEBUG
logPath = "./"
fileName = "Disk"
logging.basicConfig(level=logging.DEBUG,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format(logPath, fileName)),
        logging.StreamHandler()
    ])

FILENAME = "../tests/images/Testimage.img"

def createNewFat():
    # Create instance of Disk object for further reading and writing access to image file
    # The image file has to be created before
    disk = Disk(FILENAME, 'r+b', 0)

    # Creates new fat boot sector and fsinfo objects with example values and writes structures to disk
    fat = FATCreator.mkfat32(stream=disk,
                                size=disk.size,
                                wBytesPerSector=512,
                                uchSectorsPerCluster=2,
                                chOemId='Test',
                                sVolumeLabel='Demonstrate')


if __name__ == "__main__":
    createNewFat()
