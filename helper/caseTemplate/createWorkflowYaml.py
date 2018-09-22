import argparse
import sys

import ruamel

from util.enums import PositionType
from workflow.rawSteps import *
from workflow.workflow import Workflow
from workflow.fatSteps import *
from workflow.diskSteps import *


def createWorkflowYaml(yamlPath):
    # Initialize workflow
    workflow = Workflow()

    # EXAMPLE AREA - DELETE BEFORE
    # Create RawWriteStep
    rawStep = RawWriteStep(workflow, content=b'Testing', description="Write test string", position=1, positionType=PositionType.SECTOR)
    # Create step for loading boot sector from config file an write to disk
    fatStep = FAT32CreateBootSectorStep(workflow, pathToConfig="/datadisk/Repos/github/syntheticdisc/helper/yaml/fat32.yml")

    # Adding steps to workflow
    workflow.addStep(rawStep)
    workflow.addStep(fatStep)
    # EXAMPLE AREA - DELETE BEFORE

    # Write workflow to yaml config file
    yaml = ruamel.yaml.YAML()
    with open(yamlPath, 'w') as fout:
        yaml.dump(workflow, fout)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create workflow and save to yaml file")
    parser.add_argument("destPath", help="destination path for workflow config")
    args = parser.parse_args()

    createWorkflowYaml(yamlPath=args.destPath)
