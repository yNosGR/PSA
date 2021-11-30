import json
import pulumi
import pulumi_aws

#import the other stuff we've built and need to ref.
import vpc 
import s3
#import db

# find the latest azn linux2 ami
ami = pulumi_aws.ec2.get_ami(most_recent="True",
  owners=["137112412989"],
  filters=[{"name":"name","values":["amzn2-ami-hvm-*"]}])

# create the ec2 node sg
ec2SecurityGroup = pulumi_aws.ec2.SecurityGroup(
    resource_name="ec2SecurityGroup",
    #vpc_id=vpc.shared_vpc.id,
    vpc_id=vpc.shared_vpc.id,
    egress=[pulumi_aws.ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol='-1',
        cidr_blocks=['0.0.0.0/0']
    )],
    ingress=[pulumi_aws.ec2.SecurityGroupIngressArgs(
            cidr_blocks=['0.0.0.0/0'],
            from_port=80,
            to_port=80,
            protocol='tcp',
            description='Allow internet access to instance'
        )])

#create the ec2 cloudwatch policy
cloudwatchpolicy = pulumi_aws.iam.Policy("psa-ec2-cloudwatch",
    path="/",
    description="EC2 cloudwatch policy",
    policy=json.dumps({
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogStreams"
    ],
      "Resource": [
        "*"
    ]
  }
 ]
}))

#make the ec2-instance-role
ec2InstanceRole = pulumi_aws.iam.Role("psa-ec2-attach-role",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Sid": "",
            "Principal": {
                "Service": "ec2.amazonaws.com",
            },
        }],
    })
  )

ec2InstanceRole_profile = pulumi_aws.iam.InstanceProfile("ec2-Profile", role=ec2InstanceRole.name)

#now tie them together
test_attach1 = pulumi_aws.iam.RolePolicyAttachment("test-attach1",
    role=ec2InstanceRole.name,
    policy_arn=cloudwatchpolicy.arn)

#add the easy ssm policy for good measure
test_attach2 = pulumi_aws.iam.RolePolicyAttachment("test-attach2",
    role=ec2InstanceRole.name,
    policy_arn="arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore")


#make a hello world - I dont like how I did the DB endpoint. It's a hack that assumes the dburi never changes. 
user_data = """
#!/bin/bash

count=0; until ping -c 1 ynos.us ; do count=$((count+1)) ; sleep 10; echo "cant connect to the internet for $count seconds"; done

cd
sudo yum update ; sudo yum install -y mysql awslogs
sudo amazon-linux-extras install nginx1 -y
sudo systemctl start awslogsd
sudo systemctl enable awslogsd
sudo systemctl start nginx
sudo systemctl enable nginx

whoami | logger -t whomai

mkdir mywebservice
cd mywebservice

sudo cat <<_EOF >> mywebservice.sh

test -d /usr/share/nginx/html || mkdir /usr/share/nginx/html
cd /usr/share/nginx/html
#echo "Hello, World! from " $(hostname) > index.html
while true ; do echo "Hello, World! from " $(hostname) " mysql db uptime is:"> index.html ;  mysql -upsadbuser -p'pleasedontusethishorriblepassword' -hpsa-db1.c7ttwsa3oqdo.us-east-1.rds.amazonaws.com -P 5432 --skip-column-names -B -e 'SHOW /*!50002 GLOBAL */ STATUS LIKE "Uptime"' >> index.html ; sleep 1; done | logger -t mysqlUpdater 

_EOF

chmod +x mywebservice.sh
cp mywebservice.sh /bin

cat <<_EOF >> mywebservice.service
[Unit]
Description=simple systemd service.

[Service]
Type=simple
ExecStart=/bin/bash /bin/mywebservice.sh

[Install]
WantedBy=multi-user.target

_EOF

sudo cp mywebservice.service /etc/systemd/system/mywebservice.service
sudo systemctl enable mywebservice
sudo systemctl start mywebservice

"""

#create 2 ec2 instances
ec2instances = [pulumi_aws.ec2.Instance(
    resource_name="pulumi-aws-PSA0",
    availability_zone=vpc.availableZones.names[0],
    vpc_security_group_ids=[ec2SecurityGroup.id],
    subnet_id=vpc.subnet_application0.id,
    instance_type='t2.micro',
    iam_instance_profile=ec2InstanceRole_profile.name,
    ami=ami.id,
    user_data=user_data,
    tags={
        "Name": "PSA1",
    }
),
pulumi_aws.ec2.Instance(
    resource_name="pulumi-aws-PSA1",
    availability_zone=vpc.availableZones.names[1],
    vpc_security_group_ids=[ec2SecurityGroup.id],
    subnet_id=vpc.subnet_application1.id,
    instance_type='t2.micro',
    iam_instance_profile=ec2InstanceRole_profile,
    ami=ami.id,
    user_data=user_data,
    tags={
        "Name": "PSA2",
    }
)
]

#create the lb sg
elbSecurityGroup = pulumi_aws.ec2.SecurityGroup(
    resource_name="elbSecurityGroup",
    vpc_id=vpc.shared_vpc.id,
    egress=[pulumi_aws.ec2.SecurityGroupEgressArgs(
        from_port=0,
        to_port=0,
        protocol='-1',
        cidr_blocks=['0.0.0.0/0']
    )],
    ingress=[pulumi_aws.ec2.SecurityGroupIngressArgs(
            cidr_blocks=['0.0.0.0/0'],
            from_port=80,
            to_port=80,
            protocol='tcp',
            description='Allow internet access to instance'
)])

# and now the classic lb - because it's easier
PSAelb = pulumi_aws.elb.LoadBalancer("psaELB",
    security_groups=[elbSecurityGroup.id],
    subnets=[vpc.subnet_elb0,vpc.subnet_elb1],
    access_logs=pulumi_aws.elb.LoadBalancerAccessLogsArgs(
        bucket=s3.bucket.id,
        bucket_prefix="psa-elb-logs",
        interval=60,
    ),
    listeners=[
        pulumi_aws.elb.LoadBalancerListenerArgs(
            instance_port=80,
            instance_protocol="http",
            lb_port=80,
            lb_protocol="http",
        ),
    ],
    health_check=pulumi_aws.elb.LoadBalancerHealthCheckArgs(
        healthy_threshold=2,
        unhealthy_threshold=2,
        timeout=3,
        target="HTTP:80/index.html",
        interval=30,
    ),
    instances=ec2instances,
    cross_zone_load_balancing=True,
    idle_timeout=400,
    connection_draining=True,
    connection_draining_timeout=400,
    opts=pulumi.resource.ResourceOptions(depends_on=s3.bucket),
    tags={
        "Name": "PSA-example-elb",
    })
pulumi.export('PSAelb', PSAelb.dns_name)
