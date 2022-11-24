# back-customer
## In order to create conda enviroment type the following commnad
### conda create --name envname --file requirements.txt
## In order to run the api type the following command
### python api.py

#### Example: GET /api/statistics/clicksToConvert/Device

# Requests schema
```json
[
  {
    "field": "Mobile",
    "values": [
      [0, 100], [1,24], [2,5435], [hour, number of clicks]
    ]
  },
  {
    "field": "Desktop",
    "values": [
      [0, 100], [1,24], [2,5435], [hour, number of clicks]
    ]
  }
]
```

#### Example: GET /api/statistics/clicksToConvert/Locale
```json
[
  {
    "field": "en-US",
    "values": [
      [0, 100], [1,24], [2,5435], [hour, number of clicks]
    ]
  },
  {
    "field": "ru",
    "values": [
      [0, 100], [1,24], [2,5435], [hour, number of clicks]
    ]
  }
]
```
