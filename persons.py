from flask import Blueprint, request, jsonify
from cache import cache
from connection import getConnection
import azure.filters as flt
from statistics import mean

persons = Blueprint('persons', __name__)

@persons.route('/api/metrics/persons/count/<metric>/device')
@cache.cached(timeout=1000, query_string=True)
def f1(metric:str):
	if request.method == 'GET':
		metric = metric.lower()
		available_metrics = ["clickstoconvert", "clickstoshare", "totalclicks"]
		if metric not in available_metrics:
			return "Invalid metric", 400

		day = request.args.get("timestamp")
		name = None
		if day is None:
			day = 0
		elif day == "today":
			day = 0 
		elif day == "lastweek":
			day = 6
		elif day == "lastmonth":
			day = 29
		if metric == "clickstoconvert":
			name = 'conversion'
		elif metric == "clickstoshare":
			name = 'share_experience'

		cnxn = getConnection()
		cursor = cnxn.cursor()
		# selecting all devices
		devices = ["Desktop", "Mobile", "Other"]

		out = {}
		for device in devices:
			events = cursor.execute(f"""DECLARE @day AS INT
										SET @day = (SELECT DATEPART(dy, clicked_date)
													FROM Events
													WHERE clicked_date = (SELECT MAX(clicked_date)
													FROM Events))
										SELECT Events.person_id,
												Events.event_name
										FROM Events
										INNER JOIN Persons
										ON Persons.person_id = Events.person_id
										WHERE DATEPART(dy, clicked_date) >= @day - ? AND device=?
										ORDER BY clicked_date ASC""", day, device).fetchall()
			if metric == "totalclicks":
				out[device] = len(events)
				continue

			person_dict = {}

			for event in events:
				event_name = event[1]
				person_id = event[0]
				if person_id not in person_dict:
					person_dict[person_id] = [event_name]
				else:
					person_dict[person_id].append(event_name)

			values = []
			for person_id in person_dict.keys():
				counter = 0
				for event_name in person_dict[person_id]:
					if event_name == name:
						values.append(counter)
						break
					counter += 1

			out[device] = len(values)

		cnxn.close()
		return jsonify(out)

@persons.route('/api/metrics/persons/count/<metric>/locale')
@cache.cached(timeout=1000, query_string=True)
def f2(metric:str):
	if request.method == 'GET':
		metric = metric.lower()
		available_metrics = ["clickstoconvert", "clickstoshare", "totalclicks"]
		if metric not in available_metrics:
			return "Invalid metric", 400

		day = request.args.get("timestamp")
		name = None
		if day is None:
			day = 0
		elif day == "today":
			day = 0 
		elif day == "lastweek":
			day = 6
		elif day == "lastmonth":
			day = 29
		if metric == "clickstoconvert":
			name = 'conversion'
		elif metric == "clickstoshare":
			name = 'share_experience'

		cnxn = getConnection()
		cursor = cnxn.cursor()
		# selecting all devices
		locales = cursor.execute(f"""SELECT 	TOP(?)
												locale
										FROM Persons
										GROUP BY locale
										ORDER BY COUNT(locale) DESC""", 6).fetchall()

		out = {}
		for locale in locales:
			locale = locale[0]
			events = cursor.execute(f"""DECLARE @day AS INT
										SET @day = (SELECT DATEPART(dy, clicked_date)
													FROM Events
													WHERE clicked_date = (SELECT MAX(clicked_date)
													FROM Events))
										SELECT Events.person_id,
												Events.event_name
										FROM Events
										INNER JOIN Persons
										ON Persons.person_id = Events.person_id
										WHERE DATEPART(dy, clicked_date) >= @day - ? AND locale=?
										ORDER BY clicked_date ASC""", day, locale).fetchall()
			if metric == "totalclicks":
				out[locale] = len(events)
				continue

			person_dict = {}

			for event in events:
				event_name = event[1]
				person_id = event[0]
				if person_id not in person_dict:
					person_dict[person_id] = [event_name]
				else:
					person_dict[person_id].append(event_name)

			values = []
			for person_id in person_dict.keys():
				counter = 0
				for event_name in person_dict[person_id]:
					if event_name == name:
						values.append(counter)
						break
					counter += 1

			out[locale] = len(values)

		cnxn.close()
		return jsonify(out)

@persons.route('/api/metrics/persons/all/<metric>/device')
@cache.cached(timeout=1000, query_string=True)
def f3(metric:str):
	if request.method == 'GET':
		metric = metric.lower()
		available_metrics = ["clickstoconvert", "clickstoshare"]
		if metric not in available_metrics:
			return "Invalid metric", 400

		day = request.args.get("timestamp")
		name = None
		if day is None:
			day = 0
		elif day == "today":
			day = 0 
		elif day == "lastweek":
			day = 6
		elif day == "lastmonth":
			day = 29
		if metric == "clickstoconvert":
			name = 'conversion'
		elif metric == "clickstoshare":
			name = 'share_experience'

		cnxn = getConnection()
		cursor = cnxn.cursor()
		# selecting all devices
		devices = ["Desktop", "Mobile"]

		out = {}
		for device in devices:
			events = cursor.execute(f"""DECLARE @day AS INT
										SET @day = (SELECT DATEPART(dy, clicked_date)
													FROM Events
													WHERE clicked_date = (SELECT MAX(clicked_date)
													FROM Events))
										SELECT Events.person_id,
												Events.event_name
										FROM Events
										INNER JOIN Persons
										ON Persons.person_id = Events.person_id
										WHERE DATEPART(dy, clicked_date) >= @day - ? AND device=?
										ORDER BY clicked_date ASC""", day, device).fetchall()

			person_dict = {}

			for event in events:
				event_name = event[1]
				person_id = event[0]
				if person_id not in person_dict:
					person_dict[person_id] = [event_name]
				else:
					person_dict[person_id].append(event_name)

			values = []
			for person_id in person_dict.keys():
				counter = 0
				for event_name in person_dict[person_id]:
					if event_name == name:
						values.append(counter)
						break
					counter += 1

			out[device] = {"notFiltered":{"values":values, "mean":mean(values)}, "filtered":{"values":flt.filter3(values), "mean":mean(flt.filter3(values))}}

		cnxn.close()
		return jsonify(out)

@persons.route('/api/metrics/persons/all/<metric>/locale')
@cache.cached(timeout=1000, query_string=True)
def f4(metric:str):
	if request.method == 'GET':
		metric = metric.lower()
		available_metrics = ["clickstoconvert", "clickstoshare"]
		if metric not in available_metrics:
			return "Invalid metric", 400

		day = request.args.get("timestamp")
		name = None
		if day is None:
			day = 0
		elif day == "today":
			day = 0 
		elif day == "lastweek":
			day = 6
		elif day == "lastmonth":
			day = 29
		if metric == "clickstoconvert":
			name = 'conversion'
		elif metric == "clickstoshare":
			name = 'share_experience'

		cnxn = getConnection()
		cursor = cnxn.cursor()
		# selecting all devices
		locales = cursor.execute(f"""SELECT 	TOP(?)
												locale
										FROM Persons
										GROUP BY locale
										ORDER BY COUNT(locale) DESC""", 6).fetchall()

		out = {}
		for locale in locales:
			events = cursor.execute(f"""DECLARE @day AS INT
										SET @day = (SELECT DATEPART(dy, clicked_date)
													FROM Events
													WHERE clicked_date = (SELECT MAX(clicked_date)
													FROM Events))
										SELECT Events.person_id,
												Events.event_name
										FROM Events
										INNER JOIN Persons
										ON Persons.person_id = Events.person_id
										WHERE DATEPART(dy, clicked_date) >= @day - ? AND locale=?
										ORDER BY clicked_date ASC""", day, locale[0]).fetchall()

			person_dict = {}

			for event in events:
				event_name = event[1]
				person_id = event[0]
				if person_id not in person_dict:
					person_dict[person_id] = [event_name]
				else:
					person_dict[person_id].append(event_name)

			values = []
			for person_id in person_dict.keys():
				counter = 0
				for event_name in person_dict[person_id]:
					if event_name == name:
						values.append(counter)
						break
					counter += 1
			if len(values) != 0:
				out[locale[0]] = {"notFiltered":{"values":values, "mean":mean(values)}, "filtered":{"values":flt.filter3(values), "mean":mean(flt.filter3(values))}}

		cnxn.close()
		return jsonify(out)

@persons.route('/api/metrics/persons/time/all/<metric>/device')
@cache.cached(timeout=1000, query_string=True)
def f5(metric:str):
	if request.method == 'GET':
		metric = metric.lower()
		available_metrics = ["timetoconvert", "timetoshare"]
		if metric not in available_metrics:
			return "Invalid metric", 400

		day = request.args.get("timestamp")
		name = None
		if day is None:
			day = 0
		elif day == "today":
			day = 0 
		elif day == "lastweek":
			day = 6
		elif day == "lastmonth":
			day = 29
		if metric == "timetoconvert":
			name = 'conversion'
		elif metric == "timetoshare":
			name = 'share_experience'

		cnxn = getConnection()
		cursor = cnxn.cursor()
		# selecting all devices
		devices = ["Desktop", "Mobile"]

		out = {}
		for device in devices:
			events = cursor.execute(f"""DECLARE @day AS INT
										SET @day = (SELECT DATEPART(dy, clicked_date)
													FROM Events
													WHERE clicked_date = (SELECT MAX(clicked_date)
													FROM Events))
										SELECT Events.person_id,
												Events.event_name,
												Events.clicked_date
										FROM Events
										INNER JOIN Persons
										ON Persons.person_id = Events.person_id
										WHERE DATEPART(dy, clicked_date) >= @day - ? AND device=?
										ORDER BY clicked_date ASC""", day, device).fetchall()

			person_dict = {}

			for event in events:
				event_name = event[1]
				person_id = event[0]
				date = event[2]
				if person_id not in person_dict:
					person_dict[person_id] = [[event_name, date]]
				else:
					person_dict[person_id].append([event_name, date])

			values = []
			for person_id in person_dict.keys():
				events = person_dict[person_id]
				start = events[0][1]
				for event in events:
					event_name = event[0]
					date = event[1]
					if event_name == name:
						values.append(round((date - start).total_seconds()))
						break

			out[device] = {"notFiltered":{"values":values, "mean":mean(values)}, "filtered":{"values":flt.filter3(values), "mean":mean(flt.filter3(values))}}

		cnxn.close()
		return jsonify(out)

@persons.route('/api/metrics/persons/time/all/<metric>/locale')
@cache.cached(timeout=1000, query_string=True)
def f6(metric:str):
	if request.method == 'GET':
		metric = metric.lower()
		available_metrics = ["timetoconvert", "timetoshare"]
		if metric not in available_metrics:
			return "Invalid metric", 400

		day = request.args.get("timestamp")
		name = None
		if day is None:
			day = 0
		elif day == "today":
			day = 0 
		elif day == "lastweek":
			day = 6
		elif day == "lastmonth":
			day = 29
		if metric == "timetoconvert":
			name = 'conversion'
		elif metric == "timetoshare":
			name = 'share_experience'

		cnxn = getConnection()
		cursor = cnxn.cursor()
		# selecting all devices
		locales = cursor.execute(f"""SELECT 	TOP(?)
												locale
										FROM Persons
										GROUP BY locale
										ORDER BY COUNT(locale) DESC""", 6).fetchall()

		out = {}
		for locale in locales:
			events = cursor.execute(f"""DECLARE @day AS INT
										SET @day = (SELECT DATEPART(dy, clicked_date)
													FROM Events
													WHERE clicked_date = (SELECT MAX(clicked_date)
													FROM Events))
										SELECT Events.person_id,
												Events.event_name,
												Events.clicked_date
										FROM Events
										INNER JOIN Persons
										ON Persons.person_id = Events.person_id
										WHERE DATEPART(dy, clicked_date) >= @day - ? AND locale=?
										ORDER BY clicked_date ASC""", day, locale[0]).fetchall()

			person_dict = {}

			for event in events:
				event_name = event[1]
				person_id = event[0]
				date = event[2]
				if person_id not in person_dict:
					person_dict[person_id] = [[event_name, date]]
				else:
					person_dict[person_id].append([event_name, date])

			values = []
			for person_id in person_dict.keys():
				events = person_dict[person_id]
				start = events[0][1]
				for event in events:
					event_name = event[0]
					date = event[1]
					if event_name == name:
						values.append(round((date - start).total_seconds()))
						break
			if len(values) != 0:
				out[locale[0]] = {"notFiltered":{"values":values, "mean":mean(values)}, "filtered":{"values":flt.filter3(values), "mean":mean(flt.filter3(values))}}

		cnxn.close()
		return jsonify(out)