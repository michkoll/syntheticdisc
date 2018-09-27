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
            if not os.path.exists(self.pathToConfig):
                return WorkflowLog(self, "validate", WorkflowStatus.FAILED, LogType.LOG,
                                   reason="config file not found: {0}".format(self.pathToConfig))
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

    def __init__(self, workflow, fullPath: str = None, parentDir: str = None, dirName: str = None, deleted: bool = False, description = 'Create directory',
                 mDate = None, cDate = None, aDate = None):
        super().__init__(workflow=workflow, description=description)
        self.fullPath = fullPath
        self.parentDir = parentDir
        self.dirName = dirName
        self.deleted = deleted
        self.mDate = mDate
        self.cDate = cDate
        self.aDate = aDate

    def validate(self):
        if self.fullPath is not None:
            self.parentDir = os.path.dirname(os.path.normpath(self.fullPath))
            self.dirName = os.path.basename(os.path.normpath(self.fullPath))

        if self.dirName is None:
            return WorkflowLog(self, "validate", WorkflowStatus.FAILED, logtype=LogType.VALIDATIONERROR, reason="No dirName specified.")
        elif self.parentDir is None:
            return self.returnSuccessLog(self, "validate", "No parentDir specified. Defaulting to root directory.")
        else:
            self.parentDir = self.parentDir.strip("/")
            return self.returnSuccessLog(self, "validate")

    def execute(self, disk):
        disk.seek(0)
        sFat = disk.read(disk.blocksize)
        fatBootSector = FAT32(s=sFat, stream=disk)

        decodedFat = FAT(disk, fatBootSector.boot.fatoffs, fatBootSector.boot.clusters(), 32)
        dt = Dirtable(fatBootSector.boot, decodedFat, fatBootSector.boot.dwRootCluster)

        if self.parentDir is None:
            self.parentDir = "/"
            parentdir = dt
            subdir = dt.mkdir(self.dirName)
        else:
            parentdir = dt.opendir(self.parentDir)
            if parentdir:
                subdir = parentdir.mkdir(self.dirName)
            else:
                return WorkflowLog(self, "execute", WorkflowStatus.WARN, LogType.LOG, reason="Parent directory {0} not found. Dir {1} not created.".format(self.parentDir, self.dirName))

        if any(a is not None for a in [self.mDate, self.cDate, self.aDate]):
            subdir = parentdir.opendir(self.dirName)
            pattern = '%Y-%m-%d %H:%M:%S'
            if self.mDate is not None:
                timeW = time.strptime(self.mDate, pattern)
                subdir.handle.Entry.wMDate = FATDirentry.MakeDosDate((timeW.tm_year, timeW.tm_mon, timeW.tm_mday))
                subdir.handle.Entry.wMTime = FATDirentry.MakeDosTime((timeW.tm_hour, timeW.tm_min, timeW.tm_sec))
            if self.cDate is not None:
                timeC = time.strptime(self.cDate, pattern)
                subdir.handle.Entry.wCDate = FATDirentry.MakeDosDate((timeC.tm_year, timeC.tm_mon, timeC.tm_mday))
                subdir.handle.Entry.wCTime = FATDirentry.MakeDosTime((timeC.tm_hour, timeC.tm_min, timeC.tm_sec))
            if self.aDate is not None:
                timeA = time.strptime(self.aDate, pattern)
                subdir.handle.Entry.wADate = FATDirentry.MakeDosDate((timeA.tm_year, timeA.tm_mon, timeA.tm_mday))
            subdir.handle.close()

        if self.deleted:
            parentdir.erase(self.dirName, force=True)

        return self.returnSuccessLog(self, "execute", "Created directory {0} in dir {1}. Deleted: {2}".format(self.dirName, self.parentDir, self.deleted))

    def check(self):
        return self.returnSuccessLog(self, "check", "No check implemented")

@yaml_object(yaml)
class CreateFileStep(WorkflowStep):
    yaml_tag = u'!createFile'

    def __init__(self, workflow, description="Default description", fullPath: str = None, parentDir: str = None,
                 fileName: str = None, deleted: bool = False, mDate = None, cDate = None, aDate = None, content: str = None, contentFile: str = None):
        super().__init__(workflow, description)
        self.fullPath = fullPath
        self.parentDir = parentDir
        self.fileName = fileName
        self.deleted = deleted
        self.mDate = mDate
        self.cDate = cDate
        self.aDate = aDate
        self.content = content
        self.contentFile = contentFile

    def validate(self):
        if self.fullPath is not None:
            self.parentDir = os.path.dirname(os.path.normpath(self.fullPath))
            self.fileName = os.path.basename(os.path.normpath(self.fullPath))

        if self.contentFile is not None:
            if os.path.exists(os.path.join("/datadisk/Repos/github/syntheticdisc/cases/createFat", self.contentFile)):
                self.contentFile = os.path.join("/datadisk/Repos/github/syntheticdisc/cases/createFat", self.contentFile)
                with open(self.contentFile, mode='rb') as inFile:
                    self.content = inFile.read()

        try:
            self.content = self.content.encode(encoding=FS_ENCODING)
        except AttributeError:
            pass

        if self.fileName is None:
            return WorkflowLog(self, "validate", WorkflowStatus.FAILED, logtype=LogType.VALIDATIONERROR, reason="No dirName specified.")
        elif self.parentDir is None:
            return self.returnSuccessLog(self, "validate", "No parentDir specified. Defaulting to root directory.")
        else:
            self.parentDir = self.parentDir.strip("/")
            return self.returnSuccessLog(self, "validate")

    def execute(self, disk):
        disk.seek(0)
        sFat = disk.read(disk.blocksize)
        fatBootSector = FAT32(s=sFat, stream=disk)

        decodedFat = FAT(disk, fatBootSector.boot.fatoffs, fatBootSector.boot.clusters(), 32)
        dt = Dirtable(fatBootSector.boot, decodedFat, fatBootSector.boot.dwRootCluster)

        if self.parentDir is None:
            self.parentDir = "/"
            parentdir = dt
            f = dt.create(self.fileName)
        else:
            parentdir = dt.opendir(self.parentDir)
            if parentdir:
                f = parentdir.create(self.fileName)
            else:
                return WorkflowLog(self, "execute", WorkflowStatus.WARN, LogType.LOG,
                                   reason="Parent directory {0} not found. File {1} not created.".format(self.parentDir,
                                                                                      self.fileName))

        if self.content is not None:
            f.write(self.content)
            #f.close()


        if any(a is not None for a in [self.mDate, self.cDate, self.aDate]):
            pattern = '%Y-%m-%d %H:%M:%S'
            if self.mDate is not None:
                timeW = time.strptime(self.mDate, pattern)
                f.Entry.wMDate = FATDirentry.MakeDosDate((timeW.tm_year, timeW.tm_mon, timeW.tm_mday))
                f.Entry.wMTime = FATDirentry.MakeDosTime((timeW.tm_hour, timeW.tm_min, timeW.tm_sec))
            if self.cDate is not None:
                timeC = time.strptime(self.cDate, pattern)
                f.Entry.wCDate = FATDirentry.MakeDosDate((timeC.tm_year, timeC.tm_mon, timeC.tm_mday))
                f.Entry.wCTime = FATDirentry.MakeDosTime((timeC.tm_hour, timeC.tm_min, timeC.tm_sec))
            if self.aDate is not None:
                timeA = time.strptime(self.aDate, pattern)
                f.Entry.wADate = FATDirentry.MakeDosDate((timeA.tm_year, timeA.tm_mon, timeA.tm_mday))

        if self.deleted:
            f.close()
            disk.cache_flush()
            parentdir.erase(self.fileName, force=True)



        return self.returnSuccessLog(self, "execute",
                                     "Created file {0} in dir {1}. Deleted: {2}".format(self.fileName,
                                                                                             self.parentDir,
                                                                                             self.deleted))

    def check(self):
        return self.returnSuccessLog(self, "check", "No check implemented")





