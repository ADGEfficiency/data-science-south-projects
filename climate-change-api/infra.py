import os

import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_s3 as s3


class BucketStack(cdk.Stack):
    def __init__(self, scope, id, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        bucket = s3.Bucket(
            self,
            "APIBucket",
            versioned=False,
            #  when resource is removed from the CDK stack, it will be deleted
            removal_policy=cdk.RemovalPolicy.DESTROY,
            #  bucket will be deleted if not empty
            auto_delete_objects=True,
        )
        cdk.CfnOutput(
            self, "APIBucketName", value=bucket.bucket_name, export_name="APIBucket"
        )


class PipelineStack(cdk.Stack):
    def __init__(self, scope, id, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(
            self,
            "PipelineVPC",
            max_azs=2,
        )
        cluster = ecs.Cluster(self, "PipelineCluster", vpc=vpc)

        #  needed to access the ecr repo
        security_group = ec2.SecurityGroup(
            self,
            "PipelineSecurityGroup",
            vpc=vpc,
            description="Allow all outbound traffic",
            allow_all_outbound=True,
        )

        execution_role = iam.Role(
            self,
            "ExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                ),
            ],
        )
        task_role = iam.Role(
            self,
            "TaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AWSCloudFormationReadOnlyAccess"
                ),
            ],
        )

        task_definition = ecs.FargateTaskDefinition(
            self,
            "PipelineTask",
            execution_role=execution_role,
            task_role=task_role,
            cpu=256,
            memory_limit_mib=1024,
        )

        log_group = logs.LogGroup(
            self,
            "Logs",
            retention=logs.RetentionDays.ONE_WEEK,
        )

        task_definition.add_container(
            "PipelineContainer",
            image=ecs.ContainerImage.from_asset(
                directory=".",
                file="pipeline.Dockerfile",
                platform=ecr_assets.Platform.LINUX_AMD64,
            ),
            memory_limit_mib=1024,
            cpu=256,
            logging=ecs.LogDriver.aws_logs(
                stream_prefix="PipelineContainer", log_group=log_group
            ),
        )

        rule = events.Rule(
            self, "PipelineRule", schedule=events.Schedule.cron(minute="0", hour="0")
        )

        ecs_target = targets.EcsTask(
            cluster=cluster,
            task_definition=task_definition,
            task_count=1,
            subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            platform_version=ecs.FargatePlatformVersion.VERSION1_4,
        )

        # Add the ECS task target to the rule
        rule.add_target(ecs_target)

        cdk.CfnOutput(self, "ClusterName", value=cluster.cluster_name)
        cdk.CfnOutput(
            self, "TaskDefinitionARN", value=task_definition.task_definition_arn
        )
        cdk.CfnOutput(self, "SecurityGroupID", value=security_group.security_group_id)
        cdk.CfnOutput(
            self,
            "PublicSubnets",
            value=",".join([subnet.subnet_id for subnet in vpc.public_subnets]),
        )
        cdk.CfnOutput(self, "LogGroup", value=log_group.log_group_arn)


app = cdk.App()
BucketStack(
    app,
    "BucketStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
)
PipelineStack(
    app,
    "PipelineStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
)
app.synth()
