import ruamel
from ruamel.yaml import yaml_object

from util.commonYaml import yamlObject

yaml = ruamel.yaml.YAML()

@yaml_object(yaml)
class MainConfig(yamlObject):
    yaml_tag = u'!mainConfig'
    def __init__(self, caseDir = "",
                        diskSrc: str = "disk/srcimage.img",
                        diskDest: str = "disk/destimage.img",
                        blankDisk = True,
                        workflowConfig = "conf/workflow.yml",
                        logPath = "log/log.log",
                        logLevel = 3,
                        imageSize = 256 << 20):
        self.diskSrc = diskSrc
        self.diskDest = diskDest
        self.blankDisk = blankDisk
        self.workflowConfig = workflowConfig
        self.logPath = logPath
        self.logLevel = logLevel
        self.imageSize = imageSize