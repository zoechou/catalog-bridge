def handler(event, context):
    print(event)

    statusCode = 200
    body = "Hello file-processor v2!"

    if (!event.queryStringParameters.verified):
        statusCode = 401
        body = "Authorization failed"


    response = {
        "statusCode": statusCode,
        "headers": {
            "my_header": "my_value"
        },
        "body": body
    }
    return response
