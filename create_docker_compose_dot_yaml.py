#!/usr/local/bin/python3

# read a file from command line or a .properties file and
# turn it into a docker-compose.yml file
# or at least format the fields appropriately.

import os
import re
import ruamel.yaml
import requests
from configparser import ConfigParser

cfg = ConfigParser()
cfg.read('yak_shaving.conf')

groupid = cfg.get('connect_node', 'groupid')

try:
    r = requests.get('http://169.254.169.254/latest/meta-data/public-hostname', timeout=1)
    advertised_hostname = r.text
except:
    advertised_hostname = '0.0.0.0'

file = 'connect.properties'
# TODO: Make this not hard coded.

if os.path.exists(file):
    try:
        with open(file, 'rt') as input_file:
            environment = {}
            for line in input_file:
                if re.match(r'^\s+', line):
                    #print("leading whitespace")
                    continue
                elif re.match(r'\w+', line):
                    line = line.strip()
                    line = str(line)
                    # split line on = into field/value
                    fv = re.match(r'([^\=]*)=(.*)', line)
                    field = fv.group(1)
                    field_ = re.sub(r'\.', r'_', field)
                    ufield = field_.upper()
                    dcfield = 'CONNECT_' + ufield
                    value = fv.group(2)
                    #if re.match(r'^\d', value):
                    #    value = int(value)
                    environment[dcfield] = value
                    #print("environment[" + dcfield + "] = " + value)
            environment['CONNECT_REST_ADVERTISED_HOST_NAME'] = advertised_hostname
            environment['CONNECT_GROUP_ID'] = groupid
            # TODO: pull these values from a config file
            environment['CONNECT_CONFIG_STORAGE_TOPIC'] = groupid + '-config'
            environment['CONNECT_STATUS_STORAGE_TOPIC'] = groupid + '-status'
            environment['CONNECT_OFFSET_STORAGE_TOPIC'] = groupid + '-offset'
            environment['CONNECT_LOG4J_ROOT_LOGLEVEL'] = 'INFO'
            environment['CLASSPATH'] = '/usr/share/java/monitoring-interceptors/monitoring-interceptors-6.0.1.jar'
            environment['CONNECT_PLUGIN_PATH'] = '/usr/share/java,/usr/share/confluent-hub-components'
            environment['CONNECT_REPLICATION_FACTOR'] = '3'
            environment['CONNECT_CONFIG_STORAGE_REPLICATION_FACTOR'] = '3'
            environment['CONNECT_OFFSET_STORAGE_REPLICATION_FACTOR'] = '3'
            environment['CONNECT_STATUS_STORAGE_REPLICATION_FACTOR'] = '3'
            environment['CONNECT_LOG4J_LOGGERS'] = 'org.reflections=ERROR'
            #print(environment)
        input_file.close()
    except:
        print("Can't do stuff here")
        exit()


env = {}
env['environment'] = environment

yaml = {}
yaml['version'] = '2'

version = {}
services = {}
connect = {}
connect['image'] = 'confluentinc/cp-server-connect:6.1.0'
connect['hostname'] = 'ansible-connect'
connect['container_name'] = 'ansible-connect'
connect['ports'] = ["8083:8083"]
connect['environment'] = environment
connect['volumes'] = ["/var/spooldir:/var/spooldir"]

yaml['version'] = '2'
yaml['services'] = services
services['connect'] = connect


docker_compose_file = ruamel.yaml.round_trip_dump(yaml, explicit_start=True)

forgive_me = '''    command:
      - bash
      - -c
      - |
        echo "Installing connector plugins"
        confluent-hub install --no-prompt jcustenborder/kafka-connect-spooldir:2.0.46
        echo "Launching Kafka Connect worker"
        /etc/confluent/docker/run'''

#print(forgive_me)
with open('docker-compose.yml', 'wt') as dc:
    dc.write(str(docker_compose_file))
    dc.write(forgive_me)
