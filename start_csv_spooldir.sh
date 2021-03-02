#!/bin/sh

inventory=./hosts.yml

hostname=$(cat $inventory | grep compute.amazonaws.com | head -n 1 | tr -d ':' )

# shellcheck disable=SC2016
curl $hostname:8083/connectors -X POST -H "Content-Type: application/json" -d @csv_spooldir_config.json

