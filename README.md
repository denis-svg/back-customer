# back-customer
## In order to create conda enviroment type the following commnad
### conda create --name envname --file requirements.txt
## In order to run the api type the following command
### python api.py

#### Example: GET /api/metrics/clicks/Device
#### this endpoint can also take event_name as parameter example /api/metrics/clicks/Device?event_name=conversion
#### possible event_names = [conversion, share_experience, global_footer]
#### default is conversion
```json
{ "Mobile":
    [
      {
        "period": "1AM",
        "value": 12
      },
      {
        "period": "2AM",
        "value": 14
      }
    ]
   "Desktop":
     [
        {
          "period": "1AM",
          "value": 12
        },
        {
          "period": "2AM",
          "value": 14
        }
      ]
}
```
#### Example: GET /api/metrics/clicks/Locale
#### this endpoint can also take event_name as parameter + n(number of locales it's gonna select most used) example GET /api/metrics/clicks/Locale?event_name=conversion&&n=3
#### default n = 15 and event_name=conversion
```json
{ "en-US":
    [
      {
        "period": "1AM",
        "value": 12
      },
      {
        "period": "2AM",
        "value": 14
      }
    ]
   "ru":
     [
        {
          "period": "1AM",
          "value": 12
        },
        {
          "period": "2AM",
          "value": 14
        }
      ]
}
```
#### Example: GET /api/statistics/clicks
#### ?event_name=conversion (by default)
```json
{ field:'total',
    values: [1, 41, 41,5 6, 768, 987]
```
