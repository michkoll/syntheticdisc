import enum
from enum import Enum

from ruamel.yaml import YAML, yaml_object

from util.commonYaml import yamlWorkflowObject

yaml = YAML()

@yaml_object(yaml)
class PositionType(Enum):
    BYTE = 1
    SECTOR = 2
    CLUSTER = 3

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(
            u'!Speed',
            '{}-{}'.format(node._name_, node._value_)
        )

@yaml_object(yaml)
class ErrorReason(Enum):
    NONE = 1
    NOTDEFINED = 2

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(
            u'!Speed',
            '{}-{}'.format(node._name_, node._value_)
        )

@yaml_object(yaml)
class WorkflowStatus(Enum):
    SUCCESS = 1
    FAILED = 2
    WARN = 3

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(
            u'!Speed',
            '{}-{}'.format(node._name_, node._value_)
        )

@yaml_object(yaml)
class LogType(Enum):
    LOG = 1
    VALIDATIONERROR = 2

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(
            u'!Speed',
            '{}-{}'.format(node._name_, node._value_)
        )

