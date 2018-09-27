import argparse
import logging
import os
from shutil import copyfile

from ruamel.yaml import YAML
from scripts import mkimage, createWorkflowYaml, createFat32BootYaml

from workflow.mainConfig import MainConfig

logPath = "./"
fileName = "Disk"
logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format(logPath, fileName)),
        logging.StreamHandler()
    ])

yaml = YAML()
yaml.register_class(MainConfig)

mainConfig = None
cwd = os.getcwd()

def readConfig(path):
    global mainConfig

    # deserialize fat config file
    with open(path, 'r') as inp:
        mainConfig = yaml.load(inp)

def prepareDisk():
    if mainConfig.blankDisk or os.path.exists(mainConfig.diskSrc):
        mkimage.createImageFile(mainConfig.diskDest, size=mainConfig.imageSize)
        logging.info("Created image with size {0}: {1}".format(mainConfig.imageSize, mainConfig.destDisk))
    else:
        copyfile(mainConfig.diskSrc, mainConfig.diskDest)
        logging.info("Copied image {0} to {1}".format(mainConfig.diskSrc, mainConfig.diskDest))

def prepareWorkflow():
    createWorkflowYaml.createWorkflowYaml(mainConfig.workflowConfig)
    logging.info("Created workflow configuration: {0}".format(mainConfig.workflowConfig))

def prepareBootConfig():
    createFat32BootYaml.createBootYaml(os.path.join(os.path.dirname(mainConfig.workflowConfig)))
    logging.info("Created boot sector config in path: {0}".format(os.path.dirname(mainConfig.workflowConfig)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare case")
    parser.add_argument("configPath", help="config file")
    args = parser.parse_args()

    readConfig(args.configPath)
    prepareDisk()
    prepareWorkflow()
    prepareBootConfig()
    logging.info("Finished case preparation")