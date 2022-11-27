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
#### ?event_name=conversion (by default) (conversion, share_experience)
#### ?timestamp=today (by default) (today, lastweek, lastmonth)
```json
{ "field": "total"
  "values": [1, 4154, 64 7, 86, 5, 1, 7, 3]
}
```

#### Example: GET /api/statistics/clicks/device
#### ?event_name=conversion (by default) (conversion, share_experience)
#### ?timestamp=today (by default) (today, lastweek, lastmonth)
```json
{ 
  "Mobile": [1, 4154, 64 7, 86, 5, 1, 7, 3],
  "Desktop": [1, 4154, 64 7, 86, 5, 1, 7, 3],
}
```
#### Example: GET /api/statistics/time/device
#### ?event_name=conversion (by default) (conversion, share_experience)
#### ?timestamp=today (by default) (today, lastweek, lastmonth)
```json
{ 
  "Mobile": [1, 4154, 64 7, 86, 5, 1, 7, 3],
  "Desktop": [1, 4154, 64 7, 86, 5, 1, 7, 3],
}
```

#### Example: GET /api/metrics/urls/top-pages
#### ?n=4 (number of urls that you want default is all)
```json
[
{                           				"url":"en/us",
							"uniqueClicks":1414,
							"totalClicks":5235235,
							"timeOnPageAvg":3122,
							"timeOnPageFilteredAvg":121,
							"pageBeforeConversion":144,
							"pageBeforeShare":65
}
]
```
