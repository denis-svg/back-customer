# back-customer
## In order to create conda enviroment type the following commnad
### conda create --name envname --file requirements.txt
## In order to run the api type the following command
### python api.py

#### Example: GET /api/metrics/clicks/Device

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
