import subprocess
from google.cloud import pubsub_v1
import datetime
import const
import logging
from pubsub.publisher import Publisher, getTodoPublisher
from pubsub.subscriber import Subscriber, getDoneSubscriber
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from compute.gceutil import GCEUtil
import math
import random
import sys
import time

# Use global setting for client
# 1. initialize a set of tasks
# 2. publish the task to queue
# 3. start async subscriber for Done queue
#	3.1 if done, add it to a memory(disk persist) structure
# 4. start [# worker node] of compute
# 	4.1 if failed (due to preempt), try to bring it up
# 5. list VMs with prefix
# 	5.1 if VM number is smaller < [# worker node]
#		5.1.1 if there is shutdown VM, start it
#		5.1.2 if there is no shutdown VM, create new one
#	5.2 if VM number is greater > [# worker node], do nothing

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Scheduler(object):

	def __init__(self):
		self.tasks = []
		self.dones = set() # set to track completed tasks
		self.vmrunning = set() # set to track which VMs are running
		self.vmshutdown = set() # set to track which VMs are shutdown
		self.todoPub = getTodoPublisher()
		self.doneSub = getDoneSubscriber()
		self.RUNNING_STATES = set(["RUNNING", "STAGING", "PROVISIONING", "STOPPING"]) # allow STOPPING
		logger.info("Scheduler init complete.")

	# construct list of task to execute
	# method TO BE MODIFIED
	def _createTask(self):
		for i in range(125):
			task = '%09d' % i + ' test'
			self.tasks.append(task) # task data with all params and args needed
			logger.debug('add task [{}]'.format(task))

	def _publishTask(self):
		for task in self.tasks:
			logger.info('publishing task {}'.format(task))
			self.todoPub.publish(task)

	# received callback - task has been completed
	# add the task to Done set
	def _doneCallback(self, doneTask):
		logger.debug('Entering [_doneCallback]')
		self.dones.add(doneTask)
		logger.debug('Exiting [_doneCallback]')

	# register aync callback function, which will start a separate background thread on listening
	def _registerAsyncCallback(self):
		logger.debug('Entering [_registerAsyncCallback]')
		self.doneSub.poll(self._doneCallback)
		logger.debug('Existing [_registerAsyncCallback]')

	def _createWorkerNode(self, vmName, wait=False):
		logger.debug('Entering [_createWorkerNode] {}'.format(vmName))
		gce = GCEUtil(const.PROJECT_NAME, const.VM_ZONE)
		# vmname, customtype, imagename, serviceaccount
		operation = gce.create_instance(vmName, const.VM_TYPE, const.VM_IMAGE_NAME, const.VM_COMPUTE_SERVICE_ACCOUNT)
		if wait:
			gce.wait_for_operation(operation['name'])
		logger.debug('Existing [_createWorkerNode] {}'.format(vmName))

	def _deleteWorkerNode(self, vmName, wait=False):
		gce = GCEUtil(const.PROJECT_NAME, const.VM_ZONE)
		operation = gce.delete_instance(vmName)
		if wait:
			gce.wait_for_operation(operation['name'])

	def _startWorkerNode(self, vmName, wait=False):
		logger.debug('Entering [_startWorkerNode] {}'.format(vmName))
		gce = GCEUtil(const.PROJECT_NAME, const.VM_ZONE)
		operation = gce.start_instance(vmName)
		if wait:
			gce.wait_for_operation(operation['name'])
		logger.debug('Existing [_startWorkerNode] {}'.format(vmName))


	# set default wait False, the preemptible VM seems always be able to create
	# if no resource, it will be in shutdown states; there is no need to recreate them
	def _createWorkerNodes(self, wait=False):
		logger.info('creating new worker nodes for the tasks')
		# use a fix number of thread to start the VM
		#using worker thread to start nodes in parallel
		with ThreadPoolExecutor(max_workers=5) as executor:
			future_to_rs = {executor.submit(self._createWorkerNode, '{}{}'.format(const.VM_NAME_PREFIX, seq), wait): seq for seq in range(const.WORKER_NODE_CNT)}
			for future in as_completed(future_to_rs):
				rs = future_to_rs[future]
				try:
					l = future.result()
					print(l)
				except Exception as exc:
					print('exception: %s', exc)

	# apply filter upon listing
	def _monitorWorkerNode(self):
		logger.info("Entering [_monitorWorkerNode]")
		gce = GCEUtil(const.PROJECT_NAME, const.VM_ZONE)
		instances = gce.list_instances('(name={}*)'.format(const.VM_NAME_PREFIX))
		self.vmrunning.clear()
		self.vmshutdown.clear()
		for instance in instances:
			if (instance['status'].upper() in self.RUNNING_STATES):
				self.vmrunning.add(instance['name'])
			else:
				self.vmshutdown.add(instance['name'])
			logger.info(' - ' + instance['name'] + " - " + instance['status'])
		logger.info("Entering [_monitorWorkerNode]")
		return instances

	# this is a blocking method, the main will block here until terminated by user or tasks complete
	def _monitorTillWorkComplete(self):
		logger.info("Entering [_monitorTillWorkComplete]")
		logger.info("Done tasks are : {}".format(self.dones))
		while len(self.dones) < len(self.tasks): # not yet finish all
			numDone = len(self.dones) # this value will change, take a snapshot
			numTotal = len(self.tasks)
			numUncompleted= numTotal - numDone
			logger.logo('{} tasks done, {} uncompleted, with total {} tasks'.format(numDone, numUncompleted, numTotal))
			instances = self._monitorWorkerNode()
			if len(self.vmrunning) < min(const.WORKER_NODE_CNT, numUncompleted):
				numNodeToStart = min(const.WORKER_NODE_CNT, numUncompleted) - len(self.vmrunning)
				nodeToStart = random.sample(list(self.vmshutdown), numNodeToStart)
				logger.logo('Prepare to start {} of workers with random pick {}'.format(numNodeToStart, nodeToStart))
				for node in nodeToStart:
					self._startWorkerNode(node)
			time.sleep(25)
		logger.info("Existing [_monitorTillWorkComplete]")


	def _deleteAllNodes(self, wait=False):
		# use the thread pool to execute in parallel
		# future optimization can be done to remove not used shutdown instance to future reduce cost
		allvms = self.vmrunning.union(self.vmshutdown)
		with ThreadPoolExecutor(max_workers=5) as executor:
			future_to_rs = {executor.submit(self._deleteWorkerNode, vmName, wait): vmName for vmName in allvms}
			for future in as_completed(future_to_rs):
				rs = future_to_rs[future]
				try:
					l = future.result()
					print(l)
				except Exception as exc:
					print('exception: %s', exc)


	# scheduler main function
	def start(self):
		self._createTask()
		#self._publishTask()
		self._registerAsyncCallback()
		self._createWorkerNodes()
		time.sleep(5) # allow system to response
		self._monitorTillWorkComplete()
		self._deleteAllNodes()


######## MAIN ########
engine = Scheduler()
engine.start()

# start # of thread and do work as along as there is message left in the queue.
#
# trick problem to solve is VM is running, but got preempted before work done.
# shutdown script can write unfinish event back to queue, however, the scheduler should
# be still running at that time, and schedule another worker.
#
# need to make sure all work has been done, therefore there need to be two topics:
# one monitor success job, one to monitor jobs although it might be 
