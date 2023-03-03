import boto3
import json
from botocore.vendored import requests
from boto3.dynamodb.conditions import Key, Attr
import random
from botocore.exceptions import ClientError
import logging

"""SQS"""

def getSQS():
    sqs = boto3.client('sqs')
    url = 'https://sqs.us-east-1.amazonaws.com/082937965214/RestaurantQueue'
    try:
        response = sqs.receive_message(
            QueueUrl=url,
            AttributeNames=['SentTimestamp'],
            MaxNumberOfMessages=1,
            MessageAttributeNames=['All'],
            VisibilityTimeout=0,
            WaitTimeSeconds=0
        )
        return response
    except ClientError as e:
        logging.error(e)


def deleteSQS(message):
    try:
        sqs = boto3.client('sqs')
        url = 'https://sqs.us-east-1.amazonaws.com/082937965214/RestaurantQueue'
        response = sqs.delete_message(
            QueueUrl=url,
            ReceiptHandle=message
        )
        return response
    except ClientError as e:
        logging.error(e)

"""ES"""

def elastic_search(cuisine):
    url = 'https://search-restaurants-u3ooplqo3syvgw5f6pecml6t7a.us-east-1.es.amazonaws.com/restaurants/_search?'
    headers = {'Content-Type': 'application/json'}
    query = {
        'size': 1000,
        'query':
            {
                'query_string':
                    {
                        'default_field': 'Cuisine',
                        'query': cuisine
                    }
            }
    }

    response = requests.get(url, auth=('<AUTH_USER>', '<AUTH_PASS>'), headers=headers, data=json.dumps(query))

    data = json.loads(response.content.decode('utf-8'))
    res = data['hits']['hits']

    return res

"""DynamoDB"""

def dynamo(sqs, es):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('yelp-restaurants')

    sqs_msg = sqs['Messages'][0]['MessageAttributes']

    cuisine = sqs_msg['Cuisine']['StringValue']
    num_people = sqs_msg['NumPeople']['StringValue']
    date = sqs_msg['Date']['StringValue']
    time = sqs_msg['Time']['StringValue']

    ids = []
    count = 0
    for restaurant in es:
        ids.append(restaurant['_source']['RestaurantID'])
        count += 1
    
    selected = random.sample(range(0, count), 3)

    full_msg = f'Hey! Here are some {cuisine} restaurant suggestions for {num_people} people, for {date} at {time}:\n'

    name, addr = '', ''

    count = 1
    for id in selected:
        response = table.scan(FilterExpression=Attr('id').eq(ids[id]))
        item = response['Items'][0]
        name = item['name']
        addr = item['address']

        full_msg += str(count) + '. ' + name + ' at ' + addr + '.\n'
        count += 1
    
    full_msg += 'Enjoy your meal!'

    return full_msg

"""Lambda"""

def lambda_handler(event, context):
    sqs = getSQS()

    cuisine = sqs['Messages'][0]['MessageAttributes']['Cuisine']['StringValue']
    if cuisine.lower() == 'indian':
        cuisine = 'indpak'

    es = elastic_search(cuisine)
    msg = dynamo(sqs, es)

    deleteSQS(sqs['Messages'][0]['ReceiptHandle'])
    
    client = boto3.client('ses')
    
    sender = '<SENDER_EMAIL>'
    receiver = sqs['Messages'][0]['MessageAttributes']['Email']['StringValue']
    subject = 'Here are your Dining Suggestions!'
    charset = 'UTF-8'
    
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [receiver],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': charset,
                        'Data': msg,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source=sender
        )
    except ClientError as e:
        logging.error(e)


    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }