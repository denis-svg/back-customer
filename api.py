from flask import Flask, request, jsonify
from flask_cors import CORS
import pyodbc


def getConnection():
    return pyodbc.connect("""Driver={ODBC Driver 17 for SQL Server};
                        Server=tcp:prenaissance.database.windows.net,1433;
                        Database=customerpp;Uid=alex;Pwd=Test1234;Encrypt=yes;
                        TrustServerCertificate=no;Connection Timeout=30;""")


app = Flask(__name__)
CORS(app)


@app.route('/api/metrics/clicks/device', methods=['GET'])
def metricsClicksDevice():
    if request.method == 'GET':
        event_name = request.args.get("event_name")
        if event_name is None:
            event_name = 'conversion'
        cnxn = getConnection()
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
										GROUP BY CAST(DATEPART(hour,clicked_date) AS INT)""", event_name, device).fetchall()
            values = []
            for entry in res:
                tm = "AM"
                if entry[1] > 12:
                    tm = "PM"
                values.append({"period": str(entry[1]) + tm,
                               "value": entry[0]})
            out[device] = values
        cnxn.close()
        return jsonify(out)


@app.route('/api/metrics/clicks/locale', methods=['GET'])
def metricsClicksLocale():
    if request.method == 'GET':
        event_name = request.args.get("event_name")
        n = request.args.get("n")
        if n is None:
            n = 15
        else:
            n = int(n)
        if event_name is None:
            event_name = 'conversion'
        cnxn = getConnection()
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
                values.append({"period": str(entry[1]) + tm,
                               "value": entry[0]})
            out[locale] = values
        cnxn.close()
        return jsonify(out)


@app.route('/api/statistics/<metric>/<column>', methods=['GET'])
def statisticsClicks(metric: str, column: str):
    valid_metrics = ["clicksToConvert",
                     "clicksToShare", "timeToConvert", "timeToShare"]
    if metric.lower() not in map(str.lower, valid_metrics):
        return "Invalid metric", 400

    cnxn = getConnection()
    cursor = cnxn.cursor()

    columnExists = cursor.execute(
        f"""select 1 from sys.columns where name = ? and object_id = object_id('Persons')""", column)\
        .fetchone()
    if columnExists is None:
        return "Invalid column", 400

    fields = cursor.execute(f"""with P as (
                                    select top 1000 *
                                    from Persons
                                ),
                                Groups as (
                                    select {column}, count(*) as [Count]
                                    from P
                                    group by {column}
                                )
                                select top 5 {column} from Groups
                                order by [Count] desc""").fetchall()

    result = []
    for field in fields:
        field = field[0]
        # select 100 events

        res = cursor.execute(f"""select top 100
                                    {metric}
                                from persons_metric
                                left join Persons
                                on persons_metric.person_id = Persons.person_id
                                where {metric} is not null
                                and {column} = '{field}'""").fetchall()

        result.append({"field": field, "values": [x[0] for x in res]})

    cnxn.close()
    return jsonify(result)


@app.route('/api/statistics/time/locale', methods=['GET'])
def statisticsTimeLocale():
    pass


@app.route('/api/statistics/time/device', methods=['GET'])
def statisticsTimeDevice():
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

        cnxn = getConnection()
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

            out[device] = values

        cnxn.close()
        return jsonify(out)


@app.route('/api/metrics/urls/top-pages', methods=['GET'])
def metricsUrls():
    if request.method == 'GET':
        n = request.args.get("n")

        cnxn = getConnection()
        cursor = cnxn.cursor()

        pages = cursor.execute(f"""SELECT   urL,
											unique_clicks,
											total_clicks,
											timeOnPage,
											timeOnPage_filtered,
											pageBeforeConversion,
											pageBeforeShare
									FROM Urls
									WHERE ratio_clicks < 1 AND ratio_time < (SELECT TOP(1)
									                                                ratio_time
									                                        FROM Urls
									                                        WHERE ratio_time IN (SELECT TOP(50) PERCENT
									                                                                    ratio_time
									                                                            FROM Urls
									                                                            WHERE ratio_clicks < 1 AND ratio_time IS NOT NULL
									                                                            ORDER BY ratio_time)
									                                        ORDER BY ratio_time DESC)
									ORDER BY total_clicks DESC""").fetchall()

        out = []
        if n is None:
            for page in pages:
                out.append({"url": page[0],
                            "uniqueClicks": page[1],
                            "totalClicks": page[2],
                            "timeOnPageAvg": page[3],
                            "timeOnPageFilteredAvg": page[4],
                            "pageBeforeConversion": page[5],
                            "pageBeforeShare": page[6]})
        else:
            for page in pages[0:int(n)]:
                out.append({"url": page[0],
                            "uniqueClicks": page[1],
                            "totalClicks": page[2],
                            "timeOnPageAvg": page[3],
                            "timeOnPageFilteredAvg": page[4],
                            "pageBeforeConversion": page[5],
                            "pageBeforeShare": page[6]})
        cnxn.close()
        return jsonify(out)


@app.route('/api/metrics/urls/top-products', methods=['GET'])
def metricsProducts():
    if request.method == 'GET':
        n = request.args.get("n")

        cnxn = getConnection()
        cursor = cnxn.cursor()

        pages = cursor.execute(f"""SELECT urL,
											unique_clicks,
											total_clicks,
											timeOnPage,
											timeOnPage_filtered,
											pageBeforeConversion,
											pageBeforeShare
									FROM Urls
									WHERE ratio_clicks < 1 AND urL LIKE '%.html'  AND ratio_time < (SELECT TOP(1)
									                                                ratio_time
									                                        FROM Urls
									                                        WHERE ratio_time IN (SELECT TOP(50) PERCENT
									                                                                    ratio_time
									                                                            FROM Urls
									                                                            WHERE ratio_clicks < 1 AND ratio_time IS NOT NULL AND urL LIKE '%.html' 
									                                                            ORDER BY ratio_time)
									                                        ORDER BY ratio_time DESC)
									ORDER BY total_clicks DESC""").fetchall()

        out = []
        if n is None:
            for page in pages:
                out.append({"url": page[0],
                            "uniqueClicks": page[1],
                            "totalClicks": page[2],
                            "timeOnPageAvg": page[3],
                            "timeOnPageFilteredAvg": page[4],
                            "pageBeforeConversion": page[5],
                            "pageBeforeShare": page[6]})
        else:
            for page in pages[0:int(n)]:
                out.append({"url": page[0],
                            "uniqueClicks": page[1],
                            "totalClicks": page[2],
                            "timeOnPageAvg": page[3],
                            "timeOnPageFilteredAvg": page[4],
                            "pageBeforeConversion": page[5],
                            "pageBeforeShare": page[6]})
        cnxn.close()
        return jsonify(out)


if __name__ == '__main__':
    app.run()
