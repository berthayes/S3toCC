# S3toCC
 Deploying Kafka Connect Nodes as EC2 instances for Confluent Cloud using Python, Ansible, and Docker.  
 
 Read .csv or .json files from an S3 bucket into Confluent Cloud.   

 - [The Trick](https://github.com/berthayes/S3toCC/#The-Trick)
 - [Configuring Your Environment](https://github.com/berthayes/S3toCC/#Configuring-your-environment)
 - [Creating Connect Hosts](https://github.com/berthayes/S3toCC/#Creating-Connect-Hosts)
 - [Consume schema-less JSON with Spooldir](https://github.com/berthayes/S3toCC/#Consume-schema-less-JSON-with-Spooldir)
 
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
    - The `csv2json2s3.py` script and `10_fake_names.csv` are also included for creating JSON data and also uploading it to an S3 bucket.

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
1. Make sure hosts in inventory respond to Ansible ping
    ```
    ansible -i hosts.yml -m ping all
    ```
    You should get some JSON back with a PONG in it.

1. Run Ansible playbook `all.yml` on all nodes
    ```
    ansible-playbook -i hosts.yml all.yml
    ```

    This will take around 20 minutes or so to run.

## Consume schema-less JSON with Spooldir
1. Docker should now be running so start the spooldir connect instances

     - If this is the first time running through this, you will see new topics
    created in Confluent Cloud for the connect nodes (e.g. connect-offset,
    connect-status, connect-storage).  This will confirm that the Connect
    nodes are up and running correctly.

     - Check the topic setting in the start_spooldir.sh file
        (e.g. "topic": "user_data")
        If this topic doesn't exist yet in your instance of Confluent Cloud,
        create it now.

1. Create the target topic in Confluent Cloud if you haven't done so already.

    ```
    ./start_json_spooldir.sh
    ```

    - The connector configuration and status are stored in topics in Kafka.
    If you have already started the connectors once, you won't need to run this again.
    - If you get a "Connection Refused" error, try again after waiting a few minutes before you start network troubleshooting.

1. To terminate hosts and clean up, use the AWS console.
