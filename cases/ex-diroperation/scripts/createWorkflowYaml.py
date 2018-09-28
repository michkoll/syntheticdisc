import argparse
import sys

import ruamel

from util.enums import PositionType
from workflow.rawSteps import *
from workflow.workflow import Workflow
from workflow.fatSteps import *
from workflow.diskSteps import *


def createWorkflowYaml(yamlPath):
    # Initialize workflow
    workflow = Workflow()

    diskStep = CreateImageStep(workflow, destDisk="disk/dest.img", diskSize=256 << 20,
                               description="Create new image")
    fatStep = FAT32CreateBootSectorStep(workflow, pathToConfig=os.path.join(os.path.dirname(yamlPath), "fat32.yml"),
                                        description="Create FAT32 filesystem")
    workflow.addStep(diskStep)
    workflow.addStep(fatStep)

    # Create directories for testing short and long format entries
    parentDir = CreateDirStep(workflow, dirName="Parent", description="Create dir in root dir")
    shortDir = CreateDirStep(workflow, dirName="short", description="Create short dir entry")
    longDir = CreateDirStep(workflow, dirName="ThisIsALongDirName", description="Create long dir entry")
    existingFile = CreateFileStep(workflow, fullPath="/short/content.txt", contentFile="files/content.txt",
                                  description="Copy file to disk")
    workflow.addStep(parentDir)
    workflow.addStep(shortDir)
    workflow.addStep(existingFile)
    workflow.addStep(longDir)


    # Create file with manipulated timestamps (written before created)
    childTimeDir = CreateDirStep(workflow, fullPath="/Parent/ChildTime",
                                 description="Create subdir for time manipulation")
    fileTime = CreateFileStep(workflow, fullPath="/Parent/ChildTime/time.txt", cDate="2000-01-01 12:00:00",
                              mDate="2000-01-01 11:00:00", aDate="2000-01-01 00:00:00", content=512*'Time')
    workflow.addStep(childTimeDir)
    workflow.addStep(fileTime)

    # Demonstrate deleting operations
    childDelDir = CreateDirStep(workflow, fullPath="/Parent/ChildDel", description="Create subdir for delete operation")
    nodeleteDir = CreateDirStep(workflow, fullPath="/Parent/ChildDel/nodelete", description="Create subdir")
    deletedDir = CreateDirStep(workflow, fullPath="/Parent/ChildDel/delete", deleted=True, description="Create subdir delete")
    workflow.addStep(childDelDir)
    workflow.addStep(nodeleteDir)
    workflow.addStep(deletedDir)

    # Demonstrate reallocation of dir entries and data cluster
    childRealDir = CreateDirStep(workflow, fullPath="/Parent/ChildRealloc", description="Create subdir for reallocation")
    sectorContent = 512 * 'A' + 512 * 'B' + 512 * 'C'
    deletedFile = CreateFileStep(workflow, fullPath="/Parent/ChildRealloc/LongDeletedFileName.txt",
                                 content=sectorContent, deleted=True, description="Create file for deletion")
    newFile = CreateFileStep(workflow, fullPath="/Parent/ChildRealloc/newfile.txt", description="Create reallocation file",
                             content="Das ist die Datei, die den Cluster neu belegt.")
    workflow.addStep(childRealDir)
    workflow.addStep(deletedFile)
    workflow.addStep(newFile)

    # Write workflow to yaml config file
    yaml = ruamel.yaml.YAML()
    with open(yamlPath, 'w') as fout:
        yaml.dump(workflow, fout)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create workflow and save to yaml file")
    parser.add_argument("destPath", help="destination path for workflow config")
    args = parser.parse_args()

    createWorkflowYaml(yamlPath=args.destPath)
