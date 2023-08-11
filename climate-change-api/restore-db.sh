#!/usr/bin/env bash
DB_PATH=$1
DB_BUCKET=$(aws cloudformation describe-stacks --stack-name BucketStack | jq -r ".Stacks[0].Outputs[0].OutputValue")
rm -rf $DB_PATH
litestream restore -o $DB_PATH "s3://${DB_BUCKET}/litestream"
sqlite3 $DB_PATH "select * from log;"
