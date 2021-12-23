import pulumi_aws

#see what AZs are available
availableZones = pulumi_aws.get_availability_zones(state="available")

#create the vpc
shared_vpc = pulumi_aws.ec2.Vpc(
    resource_name='TSA-aws',
    assign_generated_ipv6_cidr_block=True,
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,enable_dns_support=True,
    tags={
        "Name": "ynostsa",
    })

# create 2 app subnets
subnet_application0 = pulumi_aws.ec2.Subnet(
    resource_name='TSA-aws_application0',
    availability_zone=availableZones.names[0],
    cidr_block="10.0.11.0/24",
    map_public_ip_on_launch=False,
    vpc_id=shared_vpc.id,
    tags={
        "Name": "TSA-aws_application0",
    })

subnet_application1 = pulumi_aws.ec2.Subnet(
    resource_name='TSA-aws_application1',
    availability_zone=availableZones.names[1],
    cidr_block="10.0.21.0/24",
    map_public_ip_on_launch=False,
    vpc_id=shared_vpc.id,
    tags={
        "Name": "TSA-aws_application1",
    })

# create 2 elb subnets
subnet_elb0 = pulumi_aws.ec2.Subnet(
    resource_name='TSA-aws_elb0',
    availability_zone=availableZones.names[0],
    cidr_block="10.0.13.0/24",
    map_public_ip_on_launch=True,
    vpc_id=shared_vpc.id,
    tags={
        "Name": "TSA-aws_elb0",
    })
    
subnet_elb1 = pulumi_aws.ec2.Subnet(
    resource_name='TSA-aws_elb1',
    availability_zone=availableZones.names[1],
    cidr_block="10.0.23.0/24",
    map_public_ip_on_launch=True,
    vpc_id=shared_vpc.id,
    tags={
        "Name": "TSA-aws_elb1",
    })
    
#create 2 db subnets
subnet_database0 = pulumi_aws.ec2.Subnet(
    resource_name='TSA-aws_database',
    availability_zone=availableZones.names[0],
    cidr_block="10.0.12.0/24",
    vpc_id=shared_vpc.id,
    tags={
        "Name": "TSA-aws_database0",
    })

subnet_database1 = pulumi_aws.ec2.Subnet(
    resource_name='TSA-aws_database_2',
    availability_zone=availableZones.names[1],
    cidr_block="10.0.22.0/24",
    vpc_id=shared_vpc.id,
    tags={
        "Name": "TSA-aws_database_2",
    })

tsa_igw= pulumi_aws.ec2.InternetGateway(
    resource_name='TSA-aws-ig',
    vpc_id=shared_vpc.id,
    tags={
        "Name": "TSA-aws-ig",
    })

gateway_eip0 = pulumi_aws.ec2.Eip(
    resource_name='TSA-aws-eip0',
    vpc=True,
    tags={
        "Name": "TSA-aws_gw-eip0",
    })

gateway_eip1 = pulumi_aws.ec2.Eip(
    resource_name='TSA-aws-eip1',
    vpc=True,
    tags={
        "Name": "TSA-aws_gw-eip1",
    })

nat_gateway0 = pulumi_aws.ec2.NatGateway(
    resource_name='TSA-aws-ng0',
    allocation_id=gateway_eip0.id,
    subnet_id=subnet_elb0.id,
    tags={
      "Name": "gw NAT 0",
    })

nat_gateway1 = pulumi_aws.ec2.NatGateway(
    resource_name='TSA-aws-ng1',
    allocation_id=gateway_eip1.id,
    subnet_id=subnet_elb1.id,
    tags={
      "Name": "gw NAT 1",
    })

routetable_application0 = pulumi_aws.ec2.RouteTable(
    resource_name='TSA-aws-simple-app0',
    vpc_id=shared_vpc.id,
    routes=[
        {
            "cidrBlock": "0.0.0.0/0",
            "gatewayId": nat_gateway0.id
        }],
    tags={
      "Name": "TSA-aws-simple-app1"
    })

routetable_application1 = pulumi_aws.ec2.RouteTable(
    resource_name='TSA-aws-simple-app1',
    vpc_id=shared_vpc.id,
    routes=[
        {
            "cidrBlock": "0.0.0.0/0",
            "gatewayId": nat_gateway1.id
        }],
    tags={
      "Name": "TSA-aws-simple-app"
    })

internet_gateway = pulumi_aws.ec2.DefaultRouteTable(
    default_route_table_id=shared_vpc.default_route_table_id,
    resource_name='TSA-aws-default-gateway',
    routes=[
        {
            "cidrBlock": "0.0.0.0/0",
            "gatewayId": tsa_igw.id
        }],
    tags={
        "Name": "TSA-aws-gateway",
    })

routetable_database = pulumi_aws.ec2.RouteTable(
    resource_name='TSA-aws-database-route',
    vpc_id=shared_vpc.id,
    tags={
        "Name": "TSA-aws-database-route",
    })

routetableAssociation_application0 = pulumi_aws.ec2.RouteTableAssociation(
    resource_name='TSA-aws-simple_application0',
    subnet_id=subnet_application0.id,
    route_table_id=routetable_application0,
    )

routetableAssociation_application1 = pulumi_aws.ec2.RouteTableAssociation(
    resource_name='TSA-aws-simple_applicationi1',
    subnet_id=subnet_application1.id,
    route_table_id=routetable_application1,
    )

routetableAssociation_database0 = pulumi_aws.ec2.RouteTableAssociation(
    resource_name='TSA-aws-database0',
    subnet_id=subnet_database0.id,
    route_table_id=routetable_database.id,
    )

routetableAssociation_database1 = pulumi_aws.ec2.RouteTableAssociation(
    resource_name='TSA-aws-database1',
    subnet_id=subnet_database1.id,
    route_table_id=routetable_database.id,
    )

routetableAssociation_elb0 = pulumi_aws.ec2.RouteTableAssociation(
    resource_name='TSA-aws-simple_elb0',
    subnet_id=subnet_elb0.id,
    route_table_id=internet_gateway,
    )

routetableAssociation_elb1 = pulumi_aws.ec2.RouteTableAssociation(
    resource_name='TSA-aws-simple_elb1',
    subnet_id=subnet_elb1.id,
    route_table_id=internet_gateway,
    )

