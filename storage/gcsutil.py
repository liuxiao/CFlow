from google.cloud import storage
import logging

logger = logging.getLogger(__name__)

def download(bucket_name, source, destination):
	# Instantiates a client
	"""Downloads a blob from the bucket."""
	storage_client = storage.Client()
	bucket = storage_client.get_bucket(bucket_name)
	blob = bucket.blob(source)

	blob.download_to_filename(destination)

	logger.info('Blob {} downloaded to {}.'.format(source, destination))

def upload(bucket_name, source, destination, content_type = 'text/csv'):
	# Instantiates a client
	storage_client = storage.Client()
	bucket = storage_client.get_bucket(bucket_name)
	blob = bucket.blob(destination)

	blob.upload_from_filename(source, content_type=content_type)

	logger.info('File {} uploaded to {}.'.format(source, destination))