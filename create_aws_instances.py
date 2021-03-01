import boto3
from configparser import ConfigParser

# create a bunch of  new EC2 instance
# TODO: create command line args to specify config file at least

cfg = ConfigParser()
cfg.read('yak_shaving.conf')


def create_instance(aws_opts, node_opts, node_count):
    ec2 = boto3.resource('ec2')
    cluster_name = aws_opts['cluster_name']
    node_job = node_opts['node_job']
    security_group_id = aws_opts['security_group_id']
    volume_size = node_opts['volume_size']
    ami = aws_opts['ami']
    InstanceType = node_opts['InstanceType']
    pem = aws_opts['pem']
    Owner_Name = aws_opts['Owner_Name']
    your_email = aws_opts['your_email']

    for i in range(0, node_count):
        iteration = str(i+1)
        node_name = cluster_name + "-" + node_job + "-" + iteration
        SecurityGroupIds = []
        SecurityGroupIds.append(security_group_id)
        print("Creating Instance ", node_name)
        ec2.create_instances(
            #DryRun=True,
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/sda1',
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'VolumeSize': int(volume_size),
                        'VolumeType': 'gp2',
                        'Encrypted': False
                    }
                }
            ],
            ImageId=ami,
            MinCount=1,
            MaxCount=1,
            InstanceType=InstanceType,
            KeyName=pem,
            SecurityGroupIds=SecurityGroupIds,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': node_name
                        },
                        {
                            'Key': 'Owner_Name',
                            'Value': Owner_Name
                        },
                        {
                            'Key': 'Owner_Email',
                            'Value': your_email
                        },
                        {
                            'Key': 'node_job',
                            'Value': node_job
                        },
                        {
                            'Key': 'cluster_name',
                            'Value': cluster_name
                        }
                    ]
                }
            ]
        )
        print(node_name, " has been created")


def make_aws_common_config_dict():
    # This makes a dict of all the common aws/ec2 options
    security_group_id = cfg.get('aws_common', 'security_group_id')
    ami = cfg.get('aws_common', 'ami')
    Owner_Name = cfg.get('aws_common', 'Owner_Name')
    pem = cfg.get('aws_common', 'your_pem')
    your_email = cfg.get('aws_common', 'your_email')
    cluster_name = cfg.get('aws_common', 'cluster_name')

    aws_opts = {'security_group_id': security_group_id,
                'cluster_name': cluster_name,
                'ami': ami,
                'Owner_Name': Owner_Name,
                'pem': pem,
                'your_email': your_email
                }

    return aws_opts


def create_connect_opts():
    InstanceType = cfg.get('connect_node', 'InstanceType')
    volume_size = cfg.get('connect_node', 'volume_size')
    node_job = "connect"

    connect_node_opts = {
        'InstanceType': InstanceType,
        'volume_size': volume_size,
        'node_job': node_job
    }
    return(connect_node_opts)


if int(cfg.get('connect_node', 'node_count')) > 0:
    node_count = int(cfg.get('connect_node', 'node_count'))
    aws_opts = make_aws_common_config_dict()
    node_opts = create_connect_opts()
    create_instance(aws_opts, node_opts, node_count)

