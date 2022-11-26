from flask import Flask, request, jsonify
import pyodbc

app = Flask(__name__)


@app.route('/api/metrics/clicks/Device', methods=['GET'])
def clicksD():
	if request.method == 'GET':
		event_name = request.args.get("event_name")
		if event_name is None:
			event_name = 'conversion'
		cnxn = pyodbc.connect("""Driver={ODBC Driver 13 for SQL Server};
                        Server=tcp:prenaissance.database.windows.net,1433;
                        Database=customerpp;Uid=alex;Pwd=Test1234;Encrypt=yes;
                        TrustServerCertificate=no;Connection Timeout=30;""")
		cursor = cnxn.cursor()

		# selecting all devices
		devices = cursor.execute(f"""SELECT DISTINCT device
								FROM Persons""").fetchall()

		out = {}
		for device in devices:
			device = device[0]
			res = cursor.execute(f"""SELECT COUNT(*),
											CAST(DATEPART(hour,clicked_date) AS INT)
										FROM Events
										INNER JOIN Persons
										ON Persons.person_id = events.person_id
										WHERE Events.event_name = ? AND Persons.device = ?
										GROUP BY CAST(DATEPART(hour,clicked_date) AS INT)""", event_name ,device).fetchall()
			values = []
			for entry in res:
				tm = "AM"
				if entry[1] > 12:
					tm = "PM"
				values.append({"period":str(entry[1]) + tm,
								"value": entry[0]})
			out[device] = values
		cnxn.close()
		return jsonify(out)

@app.route('/api/metrics/clicks/Locale', methods=['GET'])
def clicksL():
	if request.method == 'GET':
		event_name = request.args.get("event_name")
		n = request.args.get("n")
		if n is None:
			n = 15
		else:
			n = int(n)
		if event_name is None:
			event_name = 'conversion'
		cnxn = pyodbc.connect("""Driver={ODBC Driver 13 for SQL Server};
                        Server=tcp:prenaissance.database.windows.net,1433;
                        Database=customerpp;Uid=alex;Pwd=Test1234;Encrypt=yes;
                        TrustServerCertificate=no;Connection Timeout=30;""")
		cursor = cnxn.cursor()

		# selecting all devices
		locales = cursor.execute(f"""SELECT 	TOP(?)
												locale
										FROM Persons
										GROUP BY locale
										ORDER BY COUNT(locale) DESC""", n).fetchall()

		out = {}
		for locale in locales:
			locale = locale[0]
			res = cursor.execute(f"""SELECT COUNT(*),
											CAST(DATEPART(hour,clicked_date) AS INT)
										FROM Events
										INNER JOIN Persons
										ON Persons.person_id = events.person_id
										WHERE Events.event_name = ? AND Persons.locale = ?
										GROUP BY CAST(DATEPART(hour,clicked_date) AS INT)""", event_name, locale).fetchall()
			values = []
			for entry in res:
				tm = "AM"
				if entry[1] > 12:
					tm = "PM"
				values.append({"period":str(entry[1]) + tm,
								"value": entry[0]})
			out[locale] = values
		cnxn.close()
		return jsonify(out)

@app.route('/api/statistics/clicks', methods=['GET'])
def statistics():
	if request.method == 'GET':
		name = request.args.get("event_name")
		day = request.args.get("timestamp")
		if day is None:
			day = 0
		elif day == "today":
			day = 0 
		elif day == "lastweek":
			day = 6
		elif day == "lastmonth":
			day = 29
		if name is None:
			name = 'conversion'

		cnxn = pyodbc.connect("""Driver={ODBC Driver 13 for SQL Server};
                        Server=tcp:prenaissance.database.windows.net,1433;
                        Database=customerpp;Uid=alex;Pwd=Test1234;Encrypt=yes;
                        TrustServerCertificate=no;Connection Timeout=30;""")
		cursor = cnxn.cursor()

		events = cursor.execute(f"""DECLARE @day AS INT
									SET @day = (SELECT DATEPART(dy, clicked_date)
												FROM Events
												WHERE clicked_date = (SELECT MAX(clicked_date)
												FROM Events))
									SELECT person_id,
											event_name
									FROM Events
									WHERE DATEPART(dy, clicked_date) >= @day - ?
									ORDER BY clicked_date ASC""", day).fetchall()

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

		out = {"field":'total', "values":values}

		cnxn.close()
		return jsonify(out)

@app.route('/api/statistics/clicks/device', methods=['GET'])
def statisticsD():
	if request.method == 'GET':
		name = request.args.get("event_name")
		day = request.args.get("timestamp")
		if day is None:
			day = 0
		elif day == "today":
			day = 0 
		elif day == "lastweek":
			day = 6
		elif day == "lastmonth":
			day = 29
		if name is None:
			name = 'conversion'

		cnxn = pyodbc.connect("""Driver={ODBC Driver 13 for SQL Server};
                        Server=tcp:prenaissance.database.windows.net,1433;
                        Database=customerpp;Uid=alex;Pwd=Test1234;Encrypt=yes;
                        TrustServerCertificate=no;Connection Timeout=30;""")
		cursor = cnxn.cursor()
		# selecting all devices
		devices = cursor.execute(f"""SELECT DISTINCT device
								FROM Persons""").fetchall()

		out = {}
		for device in devices:
			device = device[0]
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

			out[device] = values

		cnxn.close()
		return jsonify(out)

if __name__ == '__main__':
	app.run()

