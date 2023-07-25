#!/usr/bin/env bash
sqlite3 data/database.db < schema.sql
python src/download.py
DB_BUCKET=$(aws cloudformation describe-stacks --stack-name BucketStack | jq -r ".Stacks[0].Outputs[0].OutputValue")
rm ./data/database.db
litestream restore -if-replica-exists -o ./data/database.db "s3://${DB_BUCKET}/litestream"
sqlite3 data/database.db < schema.sql
litestream replicate --exec "python src/process.py" ./data/database.db "s3://${DB_BUCKET}/litestream"
