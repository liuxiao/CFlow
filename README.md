# CFLow
The framework orchestrates a simple workflow to dispatch and manage large amount of VMs(standard or preemptible), on which to execute any user provided functions, scripts or modules.

For example, to train a ML model and perform predictions on many independent datasets, user can focus only one core algorithm file, put it in and kick off a run. The ouput will be then combined. To prepare test data submitted to Kaggle challenges, with 125 parallel VMs(without GPU), the time reduced from 14 hours to 15 minutes.

# Design breakdown
*Keep things simple!*

Currently, there is no easy way for user to execute complex functions with custom packages, ML for example, on GCE, GKE, or ML Engine. Cloud function can only run simple scripts(javascript).

There are 3 parts of framework:
* a set of scripts [init.sh](https://github.com/liuxiao/CFlow/blob/master/init.sh), [startup-singal](https://github.com/liuxiao/CFlow/blob/master/startup-signal.py), [shutdown-signal](https://github.com/liuxiao/CFlow/blob/master/shutdown-signal.py) on worker node.
* [scheduler.py](https://github.com/liuxiao/CFlow/blob/master/scheduler.py), to create, monitor, delete work VM
* [task.sh](https://github.com/liuxiao/CFlow/blob/master/task/task.sh) to represent the entry point of user provided script

![Simple Design Diagram](https://lh4.googleusercontent.com/otBSb41hPP77KTPkIxZE1clOz1UH0zHv6LH7gCE6_h1FqCBZyvNmTDBuxTkoe2Ldxxx5oHfD6GLap-aJ07tl=w3094-h1880)

# How to start

1. Build a VM image for worker VM
   1. Create a standard VM
   2. Install below packages and any other required(latter can be also done in user script)
   ```bash
   sudo pip install --upgrade google-cloud-storage
   sudo pip install --upgrade google-cloud-pubsub
   sudo pip install --upgrade google-api-python-client
   ```
   3. Download [init.sh](https://github.com/liuxiao/CFlow/blob/master/init.sh) script and place it under root /
   4. Modify the script
      - where to download and where to stage the python script from GCS
      - credential json file name
   4. Shutdown the VM
   5. Goto GCP Compute Image page, create a new VM based on the disk used for this VM. The name of the image need to be updated in [const.py](https://github.com/liuxiao/CFlow/blob/master/const.py)

1. Create a service account with following permission, then download json key and place it under credential folder
   - Compute Instance Admin
   - Service Account User
   - Pub/Sub Publisher
   - Pub/Sub Subscriber
   - Storage Object Admin

1. Place your code under "task" folder; [task.sh](https://github.com/liuxiao/CFlow/blob/master/task/task.sh) is an sample script, you can use any other code
1. Review and update [const.py](https://github.com/liuxiao/CFlow/blob/master/const.py)
1. Kick off a run
```bash
python3 scheduler.py
```

# Design with Why 
- only pull based subscriber used, because push based requires valid SSL endpoint
