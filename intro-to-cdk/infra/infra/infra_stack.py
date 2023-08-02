import aws_cdk as cdk
from aws_cdk import aws_s3 as s3


class InfraStack(cdk.Stack):
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        s3.Bucket(
            self,
            "a-data-science-south-project-bucket",
            versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
