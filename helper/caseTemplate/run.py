import argparse
import logging
import os
from shutil import copyfile

from scripts import runWorkflow, mkimage
from ruamel.yaml import YAML
from workflow.mainConfig import MainConfig

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
    else:
        copyfile(mainConfig.diskSrc, mainConfig.diskDest)

def run():
    runWorkflow.runWorkflow(mainConfig.workflowConfig, mainConfig.diskDest)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare case")
    parser.add_argument("configPath", help="config file")
    args = parser.parse_args()

    readConfig(args.configPath)

    if mainConfig.logLevel == 3:
        logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
                        handlers=[
                            logging.FileHandler(mainConfig.logPath),
                            logging.StreamHandler()
                        ])
    else:
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
                            handlers=[
                                logging.FileHandler(mainConfig.logPath),
                                logging.StreamHandler()
                            ])

    prepareDisk()
    run()
