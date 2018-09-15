import sys

import ruamel

from util.enums import PositionType
from workflow.rawSteps import RawWriteStep
from workflow.workflow import Workflow
from workflow.fatSteps import FAT32CreateBootSectorStep

workflow = Workflow()

rawStep = RawWriteStep(workflow, b'Testing', description="Parent", position=1, positionType=PositionType.SECTOR)
#rawStep2 = RawWriteStep(workflow, b'Testing', "Child", 1, PositionType.SECTOR)
#rawStep.addStep(rawStep2)
fatStep = FAT32CreateBootSectorStep(workflow, pathToConfig="/datadisk/Repos/github/syntheticdisc/tests/yaml/fat32.yml")
workflow.addStep(rawStep)
workflow.addStep(fatStep)

yaml = ruamel.yaml.YAML()

with open('yaml/workflowTest.yml', 'w') as fout:
    yaml.dump(workflow, fout)
