import json

# Opening JSON file
f = open('/Users/ash/Desktop/kittybot/config.json')
  
# returns JSON object as 
# a dictionary
data = json.load(f)
  
# Iterating through the json
# list
for i in data:
    print(data[i])
  
# Closing file
f.close()