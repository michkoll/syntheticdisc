import argparse
import sys

import ruamel

from util.enums import PositionType
from workflow.diskSteps import CreateImageStep
from workflow.rawSteps import RawWriteStep
from workflow.workflow import Workflow
from workflow.fatSteps import *


def main(yamlPath):
    # Initialize workflow
    workflow = Workflow()
    destDisk = "../tests/images/Testimage_new.img"

    diskStep = CreateImageStep(workflow, destDisk=destDisk, diskSize=256<<20)
    # Create RawWriteStep
    #rawStep = RawWriteStep(workflow, content=b'Testing', description="Write test string", position=1, positionType=PositionType.SECTOR)
    # Create step for loading boot sector from config file an write to disk
    fatStep = FAT32CreateBootSectorStep(workflow, pathToConfig="/datadisk/Repos/github/syntheticdisc/helper/yaml/fat32.yml")
    mkdirStep = CreateDirStep(workflow=workflow, dirName="First", description="Create first directory!")
    mkSubdirStep = CreateDirStep(workflow=workflow, parentDir="First", dirName="Subdir", description="Create subdir")
    mkSubSubdirStep = CreateDirStep(workflow=workflow, parentDir="First/Subdir", dirName="SubSubdir", description="Create sub subdir")

    # Adding steps to workflow
    workflow.addStep(diskStep)
    #workflow.addStep(rawStep)
    workflow.addStep(fatStep)
    workflow.addStep(mkdirStep)
    workflow.addStep(mkSubdirStep)
    workflow.addStep(mkSubSubdirStep)

    # Write workflow to yaml config file
    yaml = ruamel.yaml.YAML()
    with open(yamlPath, 'w') as fout:
        yaml.dump(workflow, fout)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create workflow and save to yaml file")
    parser.add_argument("destPath", help="destination path for workflow config")
    args = parser.parse_args()

    main(yamlPath=args.destPath)
