import googleapiclient.discovery
import logging
import time

# The API can be more generic, allowing project and zone to be supplied
# generic API allow operations across different projects and zones
#
# For this project, assume we only operate within one project and one zone
# because the amount of data we have to copy, which avoid across zones

logger = logging.getLogger(__name__)

class GCEUtil(object):
	def __init__(self, project, zone):
		self.project = project
		self.zone = zone
		self.region = zone[:zone.rfind('-')]
		self.compute = googleapiclient.discovery.build('compute', 'v1')
		print("created GCEUtil project [{}], zone [{}], region: [{}]".format(self.project, self.zone, self.region))


	# [START list_instances]
	def list_instances(self, filter):
		result = self.compute.instances().list(project=self.project, zone=self.zone, filter=filter).execute()
		return result['items']
	# [END list_instances]

	# [START create_instance]
	def create_instance(self, vmname, customtype, imagename, serviceaccount):

		config = {
			'kind': 'compute#instance',
			'name': vmname,
			'zone': 'projects/{}/zones/{}'.format(self.project, self.zone),
			'machineType': 'projects/{}/zones/{}/machineTypes/{}'.format(self.project, self.zone, customtype),
			# Specify the boot disk and the image to use as a source.
			'disks': [
				{
				  'kind': 'compute#attachedDisk',
				  'type': 'PERSISTENT',
				  'boot': 'true',
				  'mode': 'READ_WRITE',
				  'autoDelete': 'true',
				  'deviceName': vmname,
				  'initializeParams': {
					'sourceImage': 'projects/{}/global/images/{}'.format(self.project, imagename),
					'diskType': 'projects/{}/zones/{}/diskTypes/pd-standard'.format(self.project, self.zone),
					'diskSizeGb': '10'
				  }
				}
			  ],

			# Specify a network interface with NAT to access the public
			# internet.
			'networkInterfaces': [
				{
				  'kind': 'compute#networkInterface',
				  'subnetwork': 'projects/{}/regions/{}/subnetworks/default'.format(self.project, self.region),
				  'accessConfigs': [
					{
					  'kind': 'compute#accessConfig',
					  'name': 'External NAT',
					  'type': 'ONE_TO_ONE_NAT',
					  'networkTier': 'PREMIUM'
					}
				  ],
				  'aliasIpRanges': []
				}
			  ],

			# Allow the instance to access cloud storage and logging.
			'serviceAccounts': [
				{
					'email': serviceaccount,
					'scopes': [
					'https://www.googleapis.com/auth/pubsub',
					'https://www.googleapis.com/auth/servicecontrol',
					'https://www.googleapis.com/auth/service.management.readonly',
					'https://www.googleapis.com/auth/logging.write',
					'https://www.googleapis.com/auth/monitoring.write',
					'https://www.googleapis.com/auth/trace.append',
					'https://www.googleapis.com/auth/devstorage.read_write'
				  ]
				}
			  ],

			'scheduling': {
				'preemptible': 'true',
				'onHostMaintenance': 'TERMINATE',
				'automaticRestart': 'false'
			},

			# Metadata is readable from the instance and allows you to
			# pass configuration from deployment scripts to instances.
			'metadata': {
				'kind': 'compute#metadata',
				'items': [{
					# Startup script is automatically executed by the
					# instance upon startup.
					'key': 'startup-script',
					'value': '/init.sh'
				},
				{
					'key': 'shutdown-script',
					'value': 'python3 /tmp/cflow/shutdown-signal.py'
				}]
			}
		}

		return self.compute.instances().insert(
			project=self.project,
			zone=self.zone,
			body=config).execute()
	# [END create_instance]

	# [START delete_instance]
	def delete_instance(self,name):
		return self.compute.instances().delete(
			project=self.project,
			zone=self.zone,
			instance=name).execute()
	# [END delete_instance]

	# [START start_instance]
	def start_instance(self, name):
		return self.compute.instances().start(
			project=self.project,
			zone=self.zone,
			instance=name).execute()
	# [END start_instance]	

	# [START stop_instance]
	def stop_instance(self, name):
		return self.compute.instances().stop(
			project=self.project,
			zone=self.zone,
			instance=name).execute()
	# [END stop_instance]

	# [START wait_for_operation]
	def wait_for_operation(self,operation):
		print('Waiting for operation to finish...')
		while True:
			result = self.compute.zoneOperations().get(
				project=self.project,
				zone=self.zone,
				operation=operation).execute()

			if result['status'] == 'DONE':
				print('done.')
				if 'error' in result:
					raise Exception(result['error'])
				return result

			time.sleep(1)
	# [END wait_for_operation]


	# [START run]
	def test(self,wait=True):
		
		instance_name = "testinstance"
		print('Creating instance.')

		# vmname, customtype, imagename, serviceaccount
		operation = self.create_instance(instance_name, "custom-4-4096", "trainernode-image", "295987392529-compute@developer.gserviceaccount.com")
		self.wait_for_operation(operation['name'])

		instances = self.list_instances("(name=test*)")
		print('Instances in project %s and zone %s:' % (self.project, self.zone))
		for instance in instances:
			print(' - ' + instance['name'] + " - " + instance['status'])

		if wait:
			input()

		operation = self.stop_instance(instance_name)
		self.wait_for_operation(operation['name'])

		instances = self.list_instances("(name=test*)")
		print('Instances in project %s and zone %s:' % (self.project, self.zone))
		for instance in instances:
			print(' - ' + instance['name'] + " - " + instance['status'])

		if wait:
			input()

		operation = self.start_instance(instance_name)
		self.wait_for_operation(operation['name'])

		instances = self.list_instances("(name=test*)")
		print('Instances in project %s and zone %s:' % (self.project, self.zone))
		for instance in instances:
			print(' - ' + instance['name'] + " - " + instance['status'])

		print('Deleting instance.')

		operation = self.delete_instance(instance_name)
		self.wait_for_operation(operation['name'])

	# [END run]