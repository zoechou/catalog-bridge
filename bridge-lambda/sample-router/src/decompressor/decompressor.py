def handler(event, context):
    '''
        please refer to aws website for event record and required response fields
        https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format
        https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-output-format
    '''
    print(event)

    try:
        statusCode = 401
        body = "Authorization failed"

        if(event.get('queryStringParameters').get('verified', False)):
            statusCode = 200
            body = "Hello decompressor!"
    except Exception as e:
        print(e)

    response = {
        "statusCode": statusCode,
        "headers": {
            "my_header": "my_value"
        },
        "body": body
    }
    return response
