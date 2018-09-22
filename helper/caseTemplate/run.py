import argparse
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
    prepareDisk()
    run()
