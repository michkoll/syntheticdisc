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

class WorkflowLog(object):
    def __init__(self, step, method, status: WorkflowStatus, logtype = LogType.LOG, reason: str = "No reason defined"):
        self.stepName = type(step).__name__
        self.status = status
        self.logtype = logtype
        self.reason = reason
        self.method = method

    def getLogString(self):
        if self.status is not WorkflowStatus.FAILED:
            return "[{0}] Step {1}:{2} successful. Message: {3}".format(self.status.name, self.stepName, self.method, self.reason)

        elif self.status == WorkflowStatus.FAILED:
            if self.logtype == LogType.VALIDATIONERROR:
                return "[{0}] Step {1}:{2} failed with {3}. Reason: {4}".format(self.status.name, self.stepName, self.method, self.logtype.name, self.reason)



yaml = YAML()

@yaml_object(yaml)
class Workflow(yamlObject):
    '''

    '''
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
                if step.hasWorkflow(self):
                    step.run(disk)
                    disk.cache_flush()
            except WorkflowValidationException as e:
                logging.error(e.msg)
                exit(1)


    def addStep(self, step):
        if not isinstance(step, WorkflowStep):
            raise TypeError("Must be of type workflowStep!")
        else:
            self.steps.append(step)

    def addLog(self, logEntry: WorkflowLog):
        if logEntry and isinstance(logEntry, WorkflowLog):
            self._log.append(logEntry)
            logging.info(logEntry.getLogString())


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

    def run(self, disk = None):
        '''
        Executes workflow step with validation and logging. Method of parent class has to be called at the end of each step.

        :param disk: Disk object for writing
        :return: None
        '''
        if disk is not None and not isinstance(disk, Disk):
            raise TypeError("Must be of type Disk or None!")
        validateResult = self.validate()
        self._workflow.addLog(validateResult)
        if validateResult.status is not WorkflowStatus.FAILED:
            disk.cache_flush()
            executeResult = self.execute(disk)
            self._workflow.addLog(executeResult)
            if executeResult.status is not WorkflowStatus.FAILED:
                disk.cache_flush()
                checkResult = self.check()
                self._workflow.addLog(checkResult)

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

    def addStep(self, step):
        if not isinstance(step, WorkflowStep):
            raise TypeError("Must be of type workflowStep!")
        else:
            self.steps.append(step)

    def hasWorkflow(self, workflow: Workflow):
        if hasattr(self, '_workflow'):
            if isinstance(self._workflow, Workflow):
                return True
        elif isinstance(workflow, Workflow):
            self._workflow = workflow
            return True
        else:
            return False

    def returnSuccessLog(self, step, methodName: str, message: str = "No message."):
        return WorkflowLog(step, methodName, WorkflowStatus.SUCCESS, LogType.LOG, reason=message)

