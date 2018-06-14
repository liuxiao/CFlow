# CFLow
The framework orchestrates a simple workflow to dispatch and manage large amount of VMs(standard or preemptible), on which to execute any user provided functions, scripts as a module.

For example, to train a ML model and perform predictions on many independent datasets(125 files, each contains 10M records), there should be an efficient way to parallel the work, so that user can focus only one core algorithm file, plugin it in and kick off a run. The ouput will be then combined. To prepare test data submitted to [Kaggle challenges](https://www.kaggle.com/c/trackml-particle-identification), with 125 parallel VMs(without GPU), the time reduced from 14 hours to 15 minutes.

# Design consideratione
*Keep things simple!*

Currently, there is no easy way to execute complex functions/codes with custom packages, ML for example, on GCE, GKE, or ML Engine. Cloud function can only run simple scripts(javascript). 

If you are using tensorflow, and need a hybrid cloud architecture, look into [Kubeflow](https://github.com/kubeflow/kubeflow).

There are 2 important scripting of framework:
- 4 scripts on worker VM:
   - [init.sh](https://github.com/liuxiao/CFlow/blob/master/init.sh) - boot script called when VM starts; built into VM image
   - [startup-singal](https://github.com/liuxiao/CFlow/blob/master/startup-signal.py) - boot script downloaded from storage, main logic happens here
   - [shutdown-signal](https://github.com/liuxiao/CFlow/blob/master/shutdown-signal.py) - called upon VM shutdown; record unfinish work
   - [task.sh](https://github.com/liuxiao/CFlow/blob/master/task/task.sh) - entry point of user provided script
- [scheduler.py](https://github.com/liuxiao/CFlow/blob/master/scheduler.py) - on different VM or from terminal console, to create, monitor, delete work VM


![Simple Design Diagram](https://drive.google.com/uc?id=1yUoPMxaNyD_J40smGI3cPOxX8olGp18a)

# How to start

1. Download the code from Github

1. Place your code inside "task" folder; [task.sh](https://github.com/liuxiao/CFlow/blob/master/task/task.sh) is an sample script, you can use any other code

1. Review and update [const.py](https://github.com/liuxiao/CFlow/blob/master/const.py)

1. Upload the whole package into Cloud Storage

1. Build a VM image for worker VM
   1. Create a standard VM
   2. Install below packages
   ```bash
   sudo pip install --upgrade google-cloud-storage
   sudo pip install --upgrade google-cloud-pubsub
   sudo pip install --upgrade google-api-python-client
   ```
   3. Download [init.sh](https://github.com/liuxiao/CFlow/blob/master/init.sh) script and place it under root /
   4. Modify the script
      - where to download and where to stage the python script from Cloud Storage
      - credential json file name
   4. Shutdown the VM
   5. Goto Compute Image console page, create a new VM based on the disk used for this VM. The name of the image need to be updated in [const.py](https://github.com/liuxiao/CFlow/blob/master/const.py)

1. Create a service account with following permission, then download json key and place it under credential folder
   - Compute Instance Admin
   - Service Account User
   - Pub/Sub Publisher
   - Pub/Sub Subscriber
   - Storage Object Admin
   
1. Use another standard VM as the controller to kick off the script or directly use the terminal console. Make sure the user execute the script has right permission.

```bash
python3 scheduler.py
```

# Limitation
- only pull based subscriber used, because push based requires valid SSL endpoint
- log on worker nodes are stored as /tmp/cflow/cflow.log; currently we do not collect logs from nodes. But should be easy to modify the sample task.sh to achieve
- pub/sub content is not clear before each run
