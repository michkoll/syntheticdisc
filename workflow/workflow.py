import sys
from abc import ABC, abstractmethod, ABCMeta

import logging
from ruamel.yaml import YAML, yaml_object, YAMLObject

from disktools.disk import Disk
from util.commonYaml import yamlObject
from util.enums import *


class WorkflowValidationException(Exception):
    def __init__(self, parameter, step, reason):
        Exception.__init__(self, "Validation error on attribute {0} in step {1}. Attribute {2}".format(parameter, step, reason))
        self.parameter = parameter
        self.step = step
        self.reason = reason
        self.msg = "Error validating attribute {0} in step {1}. Reason: {2}".format(parameter, step, reason)


yaml = YAML()

@yaml_object(yaml)
class Workflow(yamlObject):
    yaml_tag = u'!workflow'
    _log = []


    def __init__(self):
        self.steps = []
        pass

    def run(self, disk):
        if not isinstance(disk, Disk):
            raise TypeError("Must be of type Disk!")


        for step in self.steps:
            try:
                resultValidate = step.validate()
                if resultValidate is None:
                    step.run(disk)
                    step.log()
                    step.check()
                else:
                    self._log.append(result)
                    print(result.getLogString())
                    exit(1)

            except WorkflowValidationException as e:
                logging.error(e.msg)
                exit(1)


    def addStep(self, step):
        if not isinstance(step, WorkflowStep):
            raise TypeError("Must be of type workflowStep!")
        else:
            self.steps.append(step)


@yaml_object(yaml)
class WorkflowStep(yamlObject):
    '''
    Abstact base class for all step implementations. The methods validate, execute and log have to be implemented in subclasses.
    '''
    yaml_tag = u'!step'


    def __init__(self, workflow, description = "Default description"):
        super().__init__()
        if not isinstance(workflow, Workflow):
            raise TypeError("Must be of type Workflow!")
        else:
            self._workflow = workflow

        self.description = description
        self._status = None

    def run(self, disk):
        '''
        Executes workflow step with validation and logging. Method of parent class has to be called at the end of each step.

        :param disk: Disk object for writing
        :return: None
        '''
        if not isinstance(disk, Disk):
            raise TypeError("Must be of type Disk!")
        self.execute(disk)
        self.check()
        self.log()



    def validate(self):
        '''
        Validate given attributes (existence, combination)
        :return:
        '''
        raise NotImplementedError("validate {0}".format(self.__class__))

    def execute(self, disk):
        raise NotImplementedError("execute {0}".format(self.__class__))

    def check(self):
        raise NotImplementedError("check {0}".format(self.__class__))

    def log(self):
        raise NotImplementedError("log {0}".format(self.__class__))

    def addStep(self, step):
        if not isinstance(step, WorkflowStep):
            raise TypeError("Must be of type workflowStep!")
        else:
            self.steps.append(step)

class WorkflowLog(object):
    def __init__(self, step, status: WorkflowStatus, type = LogType.LOG, **kwargs):
        self.stepName = step
        self.status = status
        self.type = type
        self.kwargs  = kwargs

    def getLogString(self):
        if self.status == WorkflowStatus.SUCCESS:
            return "[{0}] Step {1} successful.".format(self.status.name, self.stepName)

        elif self.status == WorkflowStatus.FAILED:
            if self.type == LogType.VALIDATIONERROR:
                return "[{0}] Step {1} failed with {2}. Reason: {3}".format(self.status.name, self.stepName, self.type.name, self.kwargs["reason"].name)

