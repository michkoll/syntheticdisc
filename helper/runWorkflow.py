from disktools.disk import Disk
import logging
import ruamel

from filesystem.fat import FAT, FAT_Boot
from filesystem.fat32 import FAT32, FAT32_Boot
from util.enums import PositionType
from workflow.fatSteps import *
from workflow.rawSteps import RawWriteStep
from workflow.workflow import Workflow, WorkflowStep

logPath = "./"
fileName = "Disk"
logging.basicConfig(level=logging.DEBUG,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format(logPath, fileName)),
        logging.StreamHandler()
    ])

disk = Disk("../tests/images/Testimage.img", 'r+b', 0)

yaml = ruamel.yaml.YAML()

with open('yaml/workflowTest.yml', 'r') as fin:
    workflow = yaml.load(fin)

workflow.run(disk)

