def handler(event, context):
    print(event)

    try:
        statusCode = 401
        body = "Authorization failed"

        if(event.get('queryStringParameters').get('verified', False)):
            statusCode = 200
            body = "Hello decompressor  v2!"
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
