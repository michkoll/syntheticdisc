from ruamel.yaml import YAML, yaml_object

from util.enums import *
from workflow.workflow import WorkflowStep, WorkflowLog

yaml = YAML()

@yaml_object(yaml)
class RawWriteStep(WorkflowStep):
    yaml_tag = u'!rawWrite'

    def __init__(self, workflow, content, description = 'RawWriteStep', position = 0, positionType = 1):
        '''
        Initializes RawWriteStep.

        :param workflow: Parent workflow object
        :param content:  Content, that will be written to disk
        :param description: Optionals step description
        :param position: Position on disk, default: 0
        :param positionType: PositionType (Byte=1 or Sector=2), default: PositionType.BYTE
        '''
        super().__init__(workflow, description)
        self.position = 0
        self.content = content
        self.position = position
        self.positionType = positionType.value

    def execute(self, disk):
        if self.positionType == PositionType.BYTE.value:
            disk.seek(self.position, force=1)
        elif self.positionType == PositionType.SECTOR.value:
            disk.seek(self.position * disk.blocksize)
        disk.write(self.content)
        return WorkflowLog(self, "execute", WorkflowStatus.SUCCESS, LogType.LOG)

    def validate(self):
        return WorkflowLog(self, "validate", WorkflowStatus.SUCCESS, LogType.LOG)

    def check(self):
        return self.returnSuccessLog(self, "check", "No check implemented")