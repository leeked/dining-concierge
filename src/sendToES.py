import json
from decimal import Decimal

with open('manhattan_restaurants.json', 'r') as f:
    restaurants = json.load(f, parse_float=Decimal)
    with open('restaurants.json', 'w') as g:
        count = 1
        for cuisine in restaurants:
            for restaurant in restaurants[cuisine]:
                head = {"index": {"_index": "restaurants", "_id": count}}
                json.dump(head, g)
                g.write('\n')
                item = {
                    "RestaurantID": restaurant['id'],
                    "Cuisine": cuisine,
                }
                json.dump(item, g)
                g.write('\n')
                count+=1