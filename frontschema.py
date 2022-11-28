import requests
import matplotlib.pyplot as plt
from statistics import mean

# put the url that api is running on
URL = "http://127.0.0.1:5000"
timestamps = ["today", "lastweek", "lastmonth"]
timestamp = timestamps[0]
# per person metric Count
# today
new_url = URL + "/api/metrics/persons/count/clickstoconvert/device?timestamp=" + timestamp
print("requesting from " + new_url)
conversions = requests.get(new_url).json()

new_url = URL + "/api/metrics/persons/count/clicksToShare/device?timestamp=" + timestamp
print("requesting from " + new_url)
shares = requests.get(new_url).json()

new_url = URL + "/api/metrics/persons/count/totalclicks/device?timestamp=" + timestamp
print("requesting from " + new_url)
total = requests.get(new_url).json()

fig, axs = plt.subplots(3)
axs[0].bar(list(conversions.keys()), list(conversions.values()))
axs[0].set_title("count of conversions today by device")
axs[1].bar(list(shares.keys()), list(shares.values()))
axs[1].set_title("count of shares today by device")
axs[2].bar(list(total.keys()), list(total.values()))
axs[2].set_title("total clicks today by device")

plt.show()

# per person metric All
new_url = URL + "/api/metrics/persons/all/clickstoconvert/device?timestamp=" + timestamp
print("requesting from " + new_url)
conversions = requests.get(new_url).json()

new_url = URL + "/api/metrics/persons/all/clicksToShare/device?timestamp=" + timestamp
print("requesting from " + new_url)
shares = requests.get(new_url).json()

fig, axs = plt.subplots(4)
axs[0].plot([i for i in range(len(conversions['Mobile']["notFiltered"]["values"]))],conversions['Mobile']["notFiltered"]["values"])
axs[0].plot([i for i in range(len(conversions['Mobile']["filtered"]["values"]))],conversions['Mobile']["filtered"]["values"])
axs[0].set_title(f""" conversions {timestamp} by Mobile""")
axs[1].plot([i for i in range(len(shares['Mobile']["notFiltered"]["values"]))],shares['Mobile']["notFiltered"]["values"])
axs[1].plot([i for i in range(len(shares['Mobile']["filtered"]["values"]))],shares['Mobile']["filtered"]["values"])
axs[1].set_title(f" shares {timestamp} by Mobile")

axs[2].plot([i for i in range(len(conversions['Desktop']["notFiltered"]["values"]))],conversions['Desktop']["notFiltered"]["values"])
axs[2].plot([i for i in range(len(conversions['Desktop']["filtered"]["values"]))],conversions['Desktop']["filtered"]["values"])
axs[2].set_title(f""" conversions {timestamp} by Desktop""")
axs[3].plot([i for i in range(len(shares['Desktop']["notFiltered"]["values"]))],shares['Desktop']["notFiltered"]["values"])
axs[3].plot([i for i in range(len(shares['Desktop']["filtered"]["values"]))],shares['Desktop']["filtered"]["values"])
axs[3].set_title(f""" shares {timestamp} by Desktop""")

plt.show()


# per person metric  time All
new_url = URL + "/api/metrics/persons/time/all/timeToConvert/device?timestamp=" + timestamp
print("requesting from " + new_url)
conversions = requests.get(new_url).json()

new_url = URL + "/api/metrics/persons/time/all/timeToShare/device?timestamp=" + timestamp
print("requesting from " + new_url)
shares = requests.get(new_url).json()

fig, axs = plt.subplots(4)
axs[0].plot([i for i in range(len(conversions['Mobile']["notFiltered"]["values"]))],conversions['Mobile']["notFiltered"]["values"])
axs[0].plot([i for i in range(len(conversions['Mobile']["filtered"]["values"]))],conversions['Mobile']["filtered"]["values"])
axs[0].set_title(f""" time conversions {timestamp} by Mobile""")
axs[1].plot([i for i in range(len(shares['Mobile']["notFiltered"]["values"]))],shares['Mobile']["notFiltered"]["values"])
axs[1].plot([i for i in range(len(shares['Mobile']["filtered"]["values"]))],shares['Mobile']["filtered"]["values"])
axs[1].set_title(f" time shares {timestamp} by Mobile")

axs[2].plot([i for i in range(len(conversions['Desktop']["notFiltered"]["values"]))],conversions['Desktop']["notFiltered"]["values"])
axs[2].plot([i for i in range(len(conversions['Desktop']["filtered"]["values"]))],conversions['Desktop']["filtered"]["values"])
axs[2].set_title(f""" time conversions {timestamp} by Desktop""")
axs[3].plot([i for i in range(len(shares['Desktop']["notFiltered"]["values"]))],shares['Desktop']["notFiltered"]["values"])
axs[3].plot([i for i in range(len(shares['Desktop']["filtered"]["values"]))],shares['Desktop']["filtered"]["values"])
axs[3].set_title(f""" time shares {timestamp} by Desktop""")
plt.show()




