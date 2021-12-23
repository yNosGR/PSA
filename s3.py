import json
import pulumi
import pulumi_aws

# Create an AWS resource (S3 Bucket)
bucket = pulumi_aws.s3.Bucket('ynostsa',
  force_destroy = True,
  acl="log-delivery-write"
)

# Export the name of the bucket
pulumi.export('ynostsa', bucket.id)

#put something in the bucket
bucketObject = pulumi_aws.s3.BucketObject(
    'index.html',
    bucket=bucket.id,
    source=pulumi.FileAsset('index.html')
)

