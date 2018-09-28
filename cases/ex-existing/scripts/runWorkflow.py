import argparse

from disktools.disk import Disk
import logging
import ruamel
from workflow.fatSteps import *
from workflow.rawSteps import *
from workflow.diskSteps import *
from workflow.workflow import Workflow, WorkflowStep

logPath = "./"
fileName = "Disk"
logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format(logPath, fileName)),
        logging.StreamHandler()
    ])

def runWorkflow(wfConfig, disk):

    #create disk object from path
    disk = Disk(disk, 'r+b', 0)

    # yaml factory
    yaml = ruamel.yaml.YAML()

    # deserialize workflow
    with open(wfConfig, 'r') as fin:
        workflow = yaml.load(fin)

    # run workflow
    workflow.run(disk)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Executes workflow")
    parser.add_argument("workflowPath", help="path to workflow config file")
    parser.add_argument("diskPath", help="path to image file")
    args = parser.parse_args()

    runWorkflow(args.workflowPath, args.diskPath)

