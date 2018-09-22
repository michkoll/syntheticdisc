import argparse
import datetime
import os
from shutil import copyfile, rmtree

import ruamel

from workflow.mainConfig import MainConfig

OVERWRITE = True

def createDirStructure(parentPath = "cases", caseName = f"{datetime.datetime.now():%Y-%m-%d}"):
    cwd = os.getcwd()


    if os.path.isabs(parentPath):
        caseDir = os.path.join(parentPath, caseName)
    else:
        caseDir = os.path.join(cwd, parentPath, caseName)

    if OVERWRITE and os.path.exists(caseDir):
        rmtree(caseDir)

    if not os.path.exists(caseDir):
        os.makedirs(caseDir)

    subdirs = ['disk', 'conf', 'scripts', 'log', 'files']

    for subdir in subdirs:
        if not os.path.exists(os.path.join(caseDir, subdir)):
            os.makedirs(os.path.join(caseDir, subdir))

    return caseDir

def createMainConfig(caseDir):
    pathSrcDisk = os.path.join(caseDir,'disk','src.img')
    pathDestDisk = os.path.join(caseDir,'disk','dest.img')
    blankDisk = True
    workflowConfig = os.path.join(caseDir, 'conf', 'workflow.yml')
    logPath = os.path.join(caseDir, 'log', 'log.log')
    logLevel = 3
    imageSize = 256 << 20

    config = MainConfig(caseDir=caseDir, diskSrc=pathSrcDisk, diskDest=pathDestDisk, blankDisk=blankDisk,
                        workflowConfig=workflowConfig, logPath=logPath, logLevel=logLevel,
                        imageSize=imageSize)

    yaml = ruamel.yaml.YAML()
    if not os.path.exists(os.path.join(caseDir, 'conf', 'config.yml')) or OVERWRITE:
        with open(os.path.join(caseDir, 'conf', 'config.yml'), 'w') as fout:
            yaml.dump(config, fout)

def copyHelperFiles(caseDir):
    helperFiles = ['createWorkflowYaml.py', 'mkimage.py', 'createFat32BootYaml.py', 'runWorkflow.py']

    helperDir = os.path.join(os.getcwd(), 'helper', 'caseTemplate')
    f = open(os.path.join(caseDir, 'scripts', '__init__.py'), "wb")
    copyfile(os.path.join(helperDir, 'prepare.py'), os.path.join(caseDir, 'prepare.py'))
    copyfile(os.path.join(helperDir, 'run.py'), os.path.join(caseDir, 'run.py'))
    for file in helperFiles:
        copyfile(os.path.join(helperDir, file), os.path.join(caseDir, 'scripts', file))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create new case dir structure")
    parser.add_argument("parentPath", help="parent path for case")
    parser.add_argument("caseName", help="name of case")
    args = parser.parse_args()

    caseDir = createDirStructure(parentPath=args.parentPath, caseName=args.caseName)
    createMainConfig(caseDir)
    copyHelperFiles(caseDir)