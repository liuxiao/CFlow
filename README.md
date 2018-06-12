Idea is to keep design simple. When one node comes up, it is supposed to finish one task only.
Node will shutdown after task completed. To process more tasks on one node, it would be easier to just combine the small tasks into bigger one.
This is because using preempitable VM (which might not last long, in some of the case, it got shutdown in 50 seconds, or not even able to start up). If designing the system around regular VM, then it could live and process as many tasks as possible.

export GOOGLE_APPLICATION_CREDENTIALS="[PATH]"
export GOOGLE_APPLICATION_CREDENTIALS=/Users/xiao/Documents/workspace/TrackML/credentials/cloudlewisvpn-d1fa0b387151.json


sudo pip install --upgrade google-cloud-storage
sudo pip install --upgrade google-cloud-pubsub
sudo pip install --upgrade google-api-python-client

1. only pull based subscriber used, because for push based, it requires valid SSL endpoint