# S3toCC
 Deploying Kafka Connect Nodes for Confluent Cloud in AWS using Python, Ansible, and Docker.  Read .csv or .json files from an S3 bucket into Confluent Cloud.   Each host runs [S3FS](https://github.com/s3fs-fuse/s3fs-fuse) which allows the host to mount an S3 bucket as a directory, e.g. 
 ```
 s3fs your-s3-bucket /var/spooldir/
 ```
This command will mount your S3 bucket to the /var/spooldir directory on the local filesystem.

 The host runs Kafka Connect as a Docker container with the S3 mounted directory, `/var/spooldir`
mounted as a volume within Docker.  Kafka Connect runs the [Spooldir](https://www.confluent.io/hub/jcustenborder/kafka-connect-spooldir) connector, which reads a variety of delimited files from a local directory into Apache Kafka.

The result of this little hack is that multiple Connect nodes can run Spooldir and read delimited files directly from an S3 bucket.  `W00t!`

0. In your Confluent Cloud console, go to 
    - Tools & client config -> Kafka Connect
    - Click Distributed
    - Click Create Kafka Cluster API key & secret (if you don't already have a key) and give it a description.
    - Click Create Schema Registry API key & secret and give it a description
    - Click Generate config
    - Clicking Copy will copy the generated config to your clipboard
    - Copy and Paste this auto-generated config to a file named `connect.properties`

0. Edit the config file according to your environment:
    vim yak_shaving.conf

    Be sure to change:
        security_group_id
        owner_name
        your_pem
        your_email
        cluster_name

0. Make sure there's data in your S3 bucket /input directory!
    - The connector will fail without at least one sample input file file in here.
    - The connector auto-creates a schema at startup, so it needs data to read.
    - The `create_many_sample_csv.py` script and `shorter_urls.txt` file are
    included to create sample data - 100 csv files by default.
    - The `csv2json2s3.py` script and `10_fake_names.csv` are also included for creating JSON data and also uploading it to an S3 bucket.

0. Create AWS instances
    ```
    python3 create_aws_instances.py
    ```

0. Wait a minute or two for EC2 hosts to spin up.
    Maybe pet the dog/cat.

0. Create hosts.yml inventory file for Ansible
    ```
    python3 create_hosts_dot_yaml.py
    ```
0. Make sure hosts in inventory respond to Ansible ping
    ```
    ansible -i hosts.yml -m ping all
    ```
    You should get some JSON back with a PONG in it.

0. Make sure you have a `passwd-s3fs` file in this directory

    https://github.com/s3fs-fuse/s3fs-fuse#examples

0. Edit the `all.yml` playbook and replace `your-s3bucket` with an actual S3 bucket on line 28

0. Run Ansible playbook `all.yml` on all nodes
    ```
    ansible-playbook -i hosts.yml all.yml
    ```

    This will take _a little while_ to run.

0. Docker should now be running so start the spooldir connect instances

     - If this is the first time running through this, you will see new topics
    created in Confluent Cloud for the connect nodes (e.g. connect-offset,
    connect-status, connect-storage).  This will confirm that the Connect
    nodes are up and running correctly.

     - Check the topic setting in the start_spooldir.sh file
        (e.g. "topic": "clickstream")
        If this topic doesn't exist yet in your instance of Confluent Cloud,
        create it now.

0. (Make sure there is data waiting in your S3 bucket /input directory)

0. Create the target topic in Confluent Cloud if you haven't done so already.

    ```
    ./start_json_spooldir.sh
    ```

    - The connector configuration and status are stored in topics in Kafka.
    If you have already started the connectors once, you won't need to run this again.
    - If you get a "Connection Refused" error, try again after waiting a few minutes before you start network troubleshooting.

0. Cleanup (optional) Run the terminator script to terminate running EC2 nodes
    Aaaannd.. I just terminated almost ALL of my EC2 hosts, not just the ones in this cluster.  I'm removing the terminator.py script for now.  To clean up, use the AWS console.


TODO: Include ccloud CLI usage to create connect.properties file programatically



