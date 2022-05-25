import requests


payload = {
    'lon': 127.0554836,
    'lat': 37.2863722,
    'placeID': 10780,
}

response = requests.post('http://{host}/inference/{ch}'.format(host='127.0.0.1:0', ch='byp'), json=payload)
response = dict(response.json())
print(response)