import json

data = json.load(open('manhattan_restaurants.json'))

for cuisine in data:
    print(f"{cuisine}: {len(data[cuisine])}")