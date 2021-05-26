def handler(event, context):
    print(event)

    statusCode = 401
    body = "Authorization failed"

    if (event.get('queryStringParameters', {}).get('verified', False)):
        statusCode = 200
        body = "Hello file-processor v2!"

    response = {
        "statusCode": statusCode,
        "headers": {
            "my_header": "my_value"
        },
        "body": body
    }
    return response
