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



if __name__ == '__main__':
	app.run()

