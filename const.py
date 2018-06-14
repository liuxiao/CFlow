#Number of parallel work node
WORKER_NODE_CNT = 25

#GCP
PROJECT_NAME = "cloudlewisvpn"

#CONSTANT for Compute
VM_NAME_PREFIX = "traintest-"
VM_IMAGE_NAME = "trainernode-image"
VM_TYPE = "custom-4-4096"
VM_ZONE = "us-west1-a"
VM_COMPUTE_SERVICE_ACCOUNT="295987392529-compute@developer.gserviceaccount.com"

################ CHANGE WITH CAUTIOUS ###############
#Task Module
TASK_MODULE_CMD = "/tmp/cflow/task/task.sh"


################ NO NEED TO CHANGE ##################
#Task Metadata
MARKER_EVENT_FILE = "/tmp/cflow/.task-marker"
#CONSTANT for PubSub
TOPIC_NAME_TODO = "work-todo"
TOPIC_NAME_DONE = "work-done"
SUB_TODO_NAME = "sub-todo"
SUB_DONE_NAME = "sub-done"