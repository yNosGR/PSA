import pulumi
import pulumi_aws

import ec2
import vpc
import s3

databaseSecurityGroup = pulumi_aws.ec2.SecurityGroup(
    resource_name="PSA-db-sg",
    vpc_id=vpc.shared_vpc.id)

databaseSecurityGroupRule = pulumi_aws.ec2.SecurityGroupRule(
    resource_name="PSA-db-sg-rule",
    security_group_id=databaseSecurityGroup.id,
    source_security_group_id=ec2.ec2SecurityGroup.id,
    protocol="tcp",
    from_port=5432,
    to_port=5432,
    type="ingress"
    )

subnetGroup = pulumi_aws.rds.SubnetGroup(
    resource_name="psa-db-sn-group",
    subnet_ids=[vpc.subnet_database0.id, vpc.subnet_database1.id]
)

database = pulumi_aws.rds.Instance(
    resource_name="psa-db",
    db_subnet_group_name=subnetGroup,
    allocated_storage=20,
    port=5432,
    storage_type="gp2",
    engine="mysql",
    engine_version="8.0.23",
    instance_class="db.t2.micro",
    name="pulumiAwsExample",
    identifier="psa-db1",
    username="psadbuser",
    password="pleasedontusethishorriblepassword",
    apply_immediately=False,
    final_snapshot_identifier="psa-db1-final",
    skip_final_snapshot=True,
    vpc_security_group_ids=[databaseSecurityGroup.id]
)

pulumi.export('psa-db', database.endpoint)


