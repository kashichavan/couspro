import json

with open('cleaned_data.json', 'r') as f:
    data = json.load(f)

user_ids = set()
cleaned_data = []

for entry in data:
    if entry['model'] == 'accounts.counselorprofile':
        user_id = entry['fields']['user']
        if user_id in user_ids:
            continue  # Skip duplicate
        user_ids.add(user_id)
    cleaned_data.append(entry)

with open('cleaned_data.json', 'w') as f:
    json.dump(cleaned_data, f, indent=2)

print("Duplicates removed. Cleaned data saved to 'cleaned_data.json'")