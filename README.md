# back-customer
## In order to create conda enviroment type the following commnad
### conda create --name envname --file requirements.txt
## In order to run the api type the following command
### python api.py

#### Example: GET /api/statistics/clicksToConvert/Device

```json
[
  {
    "field": "Mobile",
    "values": [
      100, 24, 5435, ...
    ]
  },
  {
    "field": "Desktop",
    "values": [
      414, 5349, 106456, ...
    ]
  }
]
```
