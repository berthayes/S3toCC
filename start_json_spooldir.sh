#!/bin/sh

inventory=./hosts.yml

hostname=$(cat $inventory | grep compute.amazonaws.com | head -n 1 | tr -d ':'| tr -d '[:space:]' )

echo $hostname

curl $hostname:8083/connectors -X POST -H "Content-Type: application/json" -d '{
	"name": "json_spooldir",
	"config": {
	  "name": "json_spooldir",
		"connector.class": "com.github.jcustenborder.kafka.connect.spooldir.SpoolDirSchemaLessJsonSourceConnector",
		"tasks.max": "1",
		"topic": "user_data",
		"input.path": "/var/spooldir/json_files",
		"finished.path": "/var/spooldir/json_finished",
		"error.path": "/var/spooldir/json_errors",
	  "input.file.pattern": ".*\\.json$",
	  "value.converter": "org.apache.kafka.connect.storage.StringConverter"
	}
}'



