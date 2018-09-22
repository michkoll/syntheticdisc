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
            return WorkflowLog(self, "validate", WorkflowStatus.FAILED, LogType.VALIDATIONERROR, reason="config path not defined")
        else:
            return WorkflowLog(self, "validate", WorkflowStatus.SUCCESS, LogType.LOG)

    def execute(self, disk):
        with open(self.pathToConfig, 'r') as fatIn:
            fatParams = yaml.load(fatIn)
        boot, fsi = FATCreator.mkfat32FromConfig(stream=disk, size=disk.size, fat32bootSectorConfig=vars(fatParams.boot),
                                                 fsInfoConfig=vars(fatParams.fsinfo))

        return  WorkflowLog(self, "execute", WorkflowStatus.SUCCESS, LogType.LOG)

    def check(self):
        return self.returnSuccessLog(self, "check", "No check implemented")

@yaml_object(yaml)
class CreateDirStep(WorkflowStep):
    yaml_tag = u'!createDir'

    def __init__(self, workflow, parentDir: str = None, dirName: str = None, deleted: bool = False, description = 'Create directory'):
        super().__init__(workflow=workflow, description=description)
        self.parentDir = parentDir
        self.dirName = dirName
        self.deleted = deleted

    def validate(self):
        if self.dirName is None:
            return WorkflowLog(self, "validate", WorkflowStatus.FAILED, logtype=LogType.VALIDATIONERROR, reason="No dirName specified.")
        elif self.parentDir is None:
            return self.returnSuccessLog(self, "validate", "No parentDir specified. Defaulting to root directory.")
        else:
            return self.returnSuccessLog(self, "validate")

    def execute(self, disk):
        disk.seek(0)
        sFat = disk.read(disk.blocksize)
        fatBootSector = FAT32(s=sFat, stream=disk)

        decodedFat = FAT(disk, fatBootSector.boot.fatoffs, fatBootSector.boot.clusters(), 32)
        dt = Dirtable(fatBootSector.boot, decodedFat, fatBootSector.boot.dwRootCluster)

        if self.parentDir is None:
            subdir = dt.mkdir(self.dirName)
            return self.returnSuccessLog(self, "execute", "Created directory {0} in root directory.".format(self.dirName))
        else:
            parentdir = dt.opendir(self.parentDir)
            findir = dt.find(self.parentDir)
            walks = dt.walk()
            if parentdir:
                subdir = parentdir.mkdir(self.dirName)
                return self.returnSuccessLog(self, "execute", "Created directory {0} in dir {1}".format(self.dirName, self.parentDir))
            else:
                return WorkflowLog(self, "execute", WorkflowStatus.WARN, LogType.LOG, reason="Parent directory {0} not found. Dir {1} not created.".format(self.parentDir, self.dirName))

        return self.returnSuccessLog(self, "execute", "No execute implemented")

    def check(self):
        return self.returnSuccessLog(self, "check", "No check implemented")

