import requests
import json

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

API_KEY = '<USER_KEY>'

cuisine_types = ['chinese', 'indpak', 'italian', 'japanese', 'korean', 'mexican']

restaurants = {}

for cuisine in cuisine_types:
    offset = 0
    restaurants[cuisine] = []
    check = set()
    while len(restaurants[cuisine]) < 1000:
        url = f'https://api.yelp.com/v3/businesses/search?categories={cuisine}&location=Manhattan&offset={offset}&limit=50'
        headers = {'Authorization': f'Bearer {API_KEY}'}
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        try:
            for business in data['businesses']:
                if business['id'] not in check:
                    restaurants[cuisine].append(business)
                
                check.add(business['id'])
            offset += 50
        except KeyError:
            print("End of category")
            print(f"Number of restaurants for {cuisine}: {len(restaurants[cuisine])}")
            break

with open('manhattan_restaurants.json', 'w') as f:
    json.dump(restaurants, f)
