from ruamel.yaml import YAML, yaml_object

from model.fat32model import *
from util.enums import *
from workflow.workflow import WorkflowStep, WorkflowValidationException, WorkflowLog
from filesystem.fat32 import *

yaml = YAML()
yaml.register_class(FAT32Parameter)
yaml.register_class(FAT32BootParameter)
yaml.register_class(FAT32FsInfoParameter)


@yaml_object(yaml)
class FAT32CreateBootSectorStep(WorkflowStep):
    yaml_tag = u'!FAT32CreateBootSector'

    def __init__(self, workflow, pathToConfig = None, description = 'Write FAT32 BootSector'):
        super().__init__(workflow, description)
        self.pathToConfig = pathToConfig

    def validate(self):
        if self.pathToConfig is None:
            self._status = WorkflowLog("Fat32BootSector", WorkflowStatus.FAILED, LogType.VALIDATIONERROR, reason=ErrorReason.NOTDEFINED)
            return self._status
            #raise WorkflowValidationException('pathToConfig', self.yaml_tag, "not defined")

    def execute(self, disk):
        with open(self.pathToConfig, 'r') as fatIn:
            fatParams = yaml.load(fatIn)
        fat = FAT32(stream=disk)
        fat.boot.mkfatFromConfig(disk.size, vars(fatParams.boot))
        fat.fsinfo.initFsInfoFromConfig(offset=0, fsInfoConfig=vars(fatParams.fsinfo))

        fat.writeNew()

        self._status = WorkflowLog("Fat32BootSector", WorkflowStatus.SUCCESS, LogType.LOG)


    def log(self):
        return self._status

    def check(self):
        pass