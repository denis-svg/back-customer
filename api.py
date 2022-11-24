from flask import Flask, request, jsonify
import pyodbc

app = Flask(__name__)

@app.route('/api/statistics/clicksToConvert/Device', methods=['GET'])
def ctcD():
	if request.method == 'GET':
		cnxn = pyodbc.connect("""Driver={ODBC Driver 13 for SQL Server};
                        Server=tcp:prenaissance.database.windows.net,1433;
                        Database=customerpp;Uid=alex;Pwd=Test1234;Encrypt=yes;
                        TrustServerCertificate=no;Connection Timeout=30;""")
		cursor = cnxn.cursor()

		# selecting all devices
		devices = cursor.execute(f"""SELECT DISTINCT device
								FROM Persons""").fetchall()

		out = []
		for device in devices:
			device = device[0]
			res = cursor.execute(f"""SELECT COUNT(*),
											CAST(DATEPART(hour,clicked_date) AS INT)
										FROM Events
										INNER JOIN Persons
										ON Persons.person_id = events.person_id
										WHERE Events.event_name = 'conversion' AND Persons.device = '{device}'
										GROUP BY CAST(DATEPART(hour,clicked_date) AS INT)""").fetchall()
			values = []
			for entry in res:
				values.append([entry[1], entry[0]])
			out.append({"field":device, "values":values})
		cnxn.close()
		return jsonify(out)

@app.route('/api/statistics/clicksToConvert/Locale', methods=['GET'])
def ctcL():
	if request.method == 'GET':
		cnxn = pyodbc.connect("""Driver={ODBC Driver 13 for SQL Server};
                        Server=tcp:prenaissance.database.windows.net,1433;
                        Database=customerpp;Uid=alex;Pwd=Test1234;Encrypt=yes;
                        TrustServerCertificate=no;Connection Timeout=30;""")
		cursor = cnxn.cursor()

		# selecting all devices
		locales = cursor.execute(f"""SELECT 	TOP(15)
												locale
										FROM Persons
										GROUP BY locale
										ORDER BY COUNT(locale) DESC""").fetchall()

		out = []
		for locale in locales:
			locale = locale[0]
			res = cursor.execute(f"""SELECT COUNT(*),
											CAST(DATEPART(hour,clicked_date) AS INT)
										FROM Events
										INNER JOIN Persons
										ON Persons.person_id = events.person_id
										WHERE Events.event_name = 'conversion' AND Persons.locale = '{locale}'
										GROUP BY CAST(DATEPART(hour,clicked_date) AS INT)""").fetchall()
			values = []
			for entry in res:
				values.append([entry[1], entry[0]])
			out.append({"field":locale, "values":values})
		cnxn.close()
		return jsonify(out)



if __name__ == '__main__':
	app.run()

