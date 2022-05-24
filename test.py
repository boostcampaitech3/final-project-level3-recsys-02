import json
import requests


payload = {
    'lat': 37.532600,
    'lon': 127.024612,
}

response = requests.post('http://{host}/inference/{ch}'.format(host='127.0.0.1:8000', ch='dhl'), json=payload)
response = dict(response.json())
data = json.loads(response['response'])
print(data)
