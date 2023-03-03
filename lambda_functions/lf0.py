import boto3

def lambda_handler(event, context):
    client = boto3.client('lex-runtime')

    response = client.post_text(
        botName='FindRestaurant',
        botAlias='DiningBot',
        userId='LF0',
        inputText=event['messages'][0]['unstructured']['text'],
    )

    package = {
        'statusCode': 200,
        'messages': [
            {
                'type': 'unstructured',
                'unstructured': {
                    'id': '00',
                    'text': response['message'],
                    'timestamp': '00-00-00'
                }
            }    
        ],
        'headers': {
            'Access-Control-Allow-Origin': '*'
        }
    }

    return package