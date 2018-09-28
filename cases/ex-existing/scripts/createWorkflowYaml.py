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
    workflow.fatLast = 0x0FFFFFFF

    copyStep = CreateImageStep(workflow, srcDisk="disk/src.img", destDisk="disk/dest.img")
    workflow.addStep(copyStep)

    delStep = CreateFileStep(workflow, fullPath="/Kontakte/besenfelder.txt", deleted=True)
    workflow.addStep(delStep)

    # Write workflow to yaml config file
    yaml = ruamel.yaml.YAML()
    with open(yamlPath, 'w') as fout:
        yaml.dump(workflow, fout)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create workflow and save to yaml file")
    parser.add_argument("destPath", help="destination path for workflow config")
    args = parser.parse_args()

    createWorkflowYaml(yamlPath=args.destPath)
