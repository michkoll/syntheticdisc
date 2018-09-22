from shutil import copyfile

from ruamel.yaml import YAML, yaml_object

from util.enums import *
from workflow.workflow import WorkflowStep, WorkflowLog


yaml = YAML()

@yaml_object(yaml)
class CreateImageStep(WorkflowStep):
    yaml_tag = u'!createImage'

    def __init__(self, workflow, description: str = "Create new blank image file",
                 srcDisk: str = None, destDisk:str = None, diskSize: int = 0):
        super().__init__(workflow=workflow, description=description)
        self.srcDisk = srcDisk
        self.destDisk = destDisk
        self.diskSize = diskSize

    def validate(self):
        if self.srcDisk is None and self.destDisk is None:
            return WorkflowLog(self, "validate", WorkflowStatus.FAILED, logtype=LogType.VALIDATIONERROR, reason="Src disk and dest disk empty.")
        if self.srcDisk is None and self.destDisk is not None and self.diskSize != 0:
            self._createBlank = True
            return WorkflowLog(self, "validate", WorkflowStatus.SUCCESS, logtype=LogType.LOG, reason="Validation result: Creating blank image")
        elif self.srcDisk is not None and self.destDisk is not None:
            self._createBlank = False
            return WorkflowLog(self, "validate", WorkflowStatus.SUCCESS, logtype=LogType.LOG, reason="Validation result: Copy image file")
        else:
            return WorkflowLog(self, "validate", WorkflowStatus.FAILED, logtype=LogType.VALIDATIONERROR, reason="Parameter combination not allowed.")

    def execute(self, disk):
        if self._createBlank:
            f = open(self.destDisk, "wb")
            f.seek(self.diskSize)
            f.truncate()
            f.close()
            return self.returnSuccessLog(self, "execute", "Blank disk with size {0} created in path {1}".format(self.diskSize, self.destDisk))
        else:
            copyfile(self.srcDisk, self.destDisk)
            return self.returnSuccessLog(self, "execute",
                                         "Blank disk copied from {0} to {1}".format(self.srcDisk,
                                                                                               self.destDisk))

    def check(self):
        return self.returnSuccessLog(self, "check", "No check implemented")

