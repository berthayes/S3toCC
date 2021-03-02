# S3toCC
 Deploying Kafka Connect Nodes as EC2 instances for Confluent Cloud using Python, Ansible, and Docker.  
 
 Read .csv or .json files from an S3 bucket into Confluent Cloud.   

 - [The Trick](https://github.com/berthayes/S3toCC/#The-Trick)
 - [Configuring Your Environment](https://github.com/berthayes/S3toCC/#Configuring-your-environment)
 - [Creating Connect Hosts](https://github.com/berthayes/S3toCC/#Creating-Connect-Hosts)
 - [Consume schema-less JSON with Spooldir](https://github.com/berthayes/S3toCC/#Consume-schema-less-JSON-with-Spooldir)
 - [Consume CSV data with schema and Confluent Cloud Schema Registry](https://github.com/berthayes/S3toCC#consume-csv-data-with-schema-and-confluent-cloud-schema-registry)
 
 ## The Trick
 Each host runs [S3FS](https://github.com/s3fs-fuse/s3fs-fuse) which allows the host to mount an S3 bucket as a directory, e.g. 
 ```
 s3fs your-s3-bucket /var/spooldir/
 ```
This command will mount your S3 bucket to the /var/spooldir directory on the local filesystem.

 Each EC2 instance runs Kafka Connect as a Docker container with the S3 mounted directory, `/var/spooldir`
mounted as a volume within Docker.  Kafka Connect runs the [Spooldir](https://www.confluent.io/hub/jcustenborder/kafka-connect-spooldir) connector, which reads delimited files from a local directory into Apache Kafka.

The result of this little hack is that multiple Connect nodes can run Spooldir and read delimited files directly from an S3 bucket.  `W00t!`


## Configuring your environment
1. In your Confluent Cloud console, go to 
    - Tools & client config -> Kafka Connect
    - Click Distributed
    - Click Create Kafka Cluster API key & secret (if you don't already have a key) and give it a description.
    - Click Create Schema Registry API key & secret and give it a description
    - Click Generate config
    - Clicking Copy will copy the generated config to your clipboard
    - Copy and Paste this auto-generated config to a file named `connect.properties` in this same directory.

1. Edit the config file according to your environment:
    ```
    vim yak_shaving.conf
    ```

    Be sure to change:
    - `security_group_id`
    - `owner_name`
    - `your_pem`
    - `your_email`
    - `cluster_name`
    - `groupid`
    - `bucket_name`

1. Make sure there's data in your S3 bucket /input directory!
    - The connector will fail without at least one sample input file in there.
    - The connector auto-creates a schema at startup, so it needs data to read.
    - The `create_many_sample_csv.py` script and `shorter_urls.txt` file are
    included to create sample data - 100 csv files by default.
    - The `csv2json2s3.py` script and `10_fake_names.csv` are included for creating JSON data and also uploading it to an S3 bucket.

1. Make sure you have a `passwd-s3fs` file in this directory.  This URL explains the format and how to generate this file:

    https://github.com/s3fs-fuse/s3fs-fuse#examples

1. Edit the `all.yml` playbook and replace `${{your-s3bucket}}` with an actual S3 bucket on line 28

## Creating Connect Hosts
1. Create AWS instances
    ```
    python3 create_aws_instances.py
    ```

1. Wait a minute or two for EC2 hosts to spin up.
    Maybe pet the dog/cat.

1. Create a `hosts.yml` inventory file for Ansible
    ```
    python3 create_hosts_dot_yaml.py
    ```
1. Make sure all hosts in inventory respond to Ansible ping
    ```
    ansible -i hosts.yml -m ping all
    ```
    You should get some JSON back with a PONG in it for each host.  If you don't get a PONG back for each host, wait a few minutes and try again.

1. Run Ansible playbook `all.yml` on all nodes
    ```
    ansible-playbook -i hosts.yml all.yml
    ```

    This will take around 20 minutes or so to run.

## Consume schema-less JSON with Spooldir
Docker should now be running so start the spooldir connect instances

If this is the first time running these steps, you will see new topics
    created in Confluent Cloud for the connect nodes (e.g. connect-offset,
    connect-status, connect-storage).  This will confirm that the Connect
    nodes are up and running correctly.

1. Make sure there are JSON files in your S3 Bucket
    - By default, this connector is configured to look for the following directories in your S3 bucket:
        - `json_files`
        - `json_errors`
        - `json_finished`
    - Sample data for manual uploading to S3 is included in the `json_files` folder of this repository.
    - The `csv2json2s3.py` script will read a csv file downloaded from [fakenamegenerator.com](https://fakenamegenerator.com) and create a JSON file for each row; each JSON file is written to a local directory as well as uploaded to the S3 bucket `json_files` folder.

1. Review the `start_json_spooldir.sh` and check topic name, folder names, etc.

1. Create the target topic in Confluent Cloud if you haven't done so already.

1. Start the connector using the supplied script
    ```
    ./start_json_spooldir.sh
    ```

    - The connector configuration and status are stored in topics in Kafka.
    If you have already started the connectors once, you won't need to run this again if your connect nodes go down/up.
    - If you get a "Connection Refused" error, try again after waiting a few minutes before you start network troubleshooting.

1. To terminate hosts and clean up, use the AWS console.

## Consume CSV data with schema and Confluent Cloud Schema Registry
1. Make sure there's data in your S3 Bucket
    - By default, this connector is configured to look for the following directories in your S3 bucket:
        - `input`
        - `errors`
        - `output`
    - The `create_many_sample_csv.py` script will use the `shorter_urls.txt` file to create 100 CSV files, each with 10 rows of data.  Each row has 2 columns, a timestamp and a [fake] URL.  This script does not (yet) upload these files to S3.
    - Sample CSV data for manual uploading to S3 is included in the `csv_files` directory of this repository.

1. Edit the connector config and start the connector
    - Option 1: Manual
        - You know what you're doing.
        - Edit the `csv_spooldir_config_template.json` file
        ```
        vim csv_spooldir_config_template.json
        ```
        - Replace values for `SCHEMAURL` and `SCHEMACREDS` with appropriate values from connect.properties files.
        - Save/copy this file as `csv_spooldir_config.json`
        - Start the connector with a script
        ```
        ./start_csv_spooldir.sh
        ```
    - Option 2: Automatic
        - Cruise Control
        - Run `create_csv_spooldir_schema_config.py`
            - This reads the connect.properties files and automagically creates a `csv_spooldir_config.json` file.
        - Start the connector with a script
        ```
        ./start_csv_spooldir.sh
        ```
1. To terminate hosts and clean up, use the AWS console.
