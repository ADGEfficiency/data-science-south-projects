#!/usr/bin/env bash
export AWS_PROFILE=sandbox
aws cloudformation describe-stacks --stack-name PipelineStack --query "Stacks[0].Outputs" > pipeline-outputs.json
cat pipeline-outputs.json

CLUSTER=$(jq -r '.[] | select(.OutputKey=="ClusterName") | .OutputValue' pipeline-outputs.json)
TASK=$(jq -r '.[] | select(.OutputKey=="TaskDefinitionARN") | .OutputValue' pipeline-outputs.json)
SUBNETS=$(jq -r '.[] | select(.OutputKey=="PublicSubnets") | .OutputValue' pipeline-outputs.json)
SECURITY_GROUP=$(jq -r '.[] | select(.OutputKey=="SecurityGroupID") | .OutputValue' pipeline-outputs.json)

echo "running ECS task on cluster: $CLUSTER, task: $TASK"

aws ecs run-task --cluster $CLUSTER --task-definition $TASK --count 1 --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SECURITY_GROUP],assignPublicIp=ENABLED}" --launch-type FARGATE > task-outputs.json

LOG_GROUP=$(jq -r '.[] | select(.OutputKey=="LogGroup") | .OutputValue' pipeline-outputs.json | awk -F ':' '{print $7}')
echo "following logs $LOG_GROUP"
awsv2 logs tail --since 1h $LOG_GROUP --profile $AWS_PROFILE --follow
