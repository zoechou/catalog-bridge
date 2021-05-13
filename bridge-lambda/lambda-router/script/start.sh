#!/usr/bin/env bash

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH/..

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

docker build -t lambda-router:latest -f docker/Dockerfile .

docker run --rm -v ~/.aws-lambda-rie:/aws-lambda -p 9000:8080 \
    --entrypoint /aws-lambda/aws-lambda-rie \
    -it lambda-router:latest \
        /usr/local/bin/python -m awslambdaric lambda_handler.handler

# curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
