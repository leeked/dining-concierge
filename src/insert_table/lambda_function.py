import json
import boto3
import datetime

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    
    table = dynamodb.Table('yelp-restaurants')

    data = json.load(open('list_manhattan_restaurants.json'))
    
    for restaurant in data:
        ts = datetime.datetime.now()
        response = table.put_item(
            Item = {
                'id': restaurant['id'],
                'insertedAtTimestamp': ts,
                'name': restaurant['name'],
                'address': restaurant['location']['address1'],
                'coordinates': restaurant['coordinates'],
                'num_reviews': restaurant['review_count'],
                'rating': restaurant['rating'],
                'zip_code': restaurant['location']['zip_code'],
                'cuisine': restaurant['categories'][0]['title'],
            })
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
