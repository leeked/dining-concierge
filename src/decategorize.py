import json

data = json.load(open('manhattan_restaurants.json'))

new_data = []

for cuisine in data:
    for restaurant in data[cuisine]:
        new_data.append(restaurant)

with open('list_manhattan_restaurants.json', 'w') as f:
    json.dump(new_data, f)