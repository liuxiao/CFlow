#!/bin/bash
mkdir /tmp/cflow
gsutil cp -r gs://trackml/cflow/* /tmp/cflow
export GOOGLE_APPLICATION_CREDENTIALS=/tmp/cflow/credential/cloudlewisvpn-14cbd880715c.json
chmod +x /tmp/cflow/*.sh
python3 /tmp/cflow/startup-signal.py &