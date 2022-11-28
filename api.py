from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_caching import Cache
import pyodbc


def getConnection():
    return pyodbc.connect("""Driver={ODBC Driver 17 for SQL Server};
                        Server=tcp:prenaissance.database.windows.net,1433;
                        Database=customerpp;Uid=alex;Pwd=Test1234;Encrypt=yes;
                        TrustServerCertificate=no;Connection Timeout=30;""")


app = Flask(__name__)
app.config["CACHE_TYPE"] = 'simple'
cache = Cache()
cache.init_app(app)

CORS(app)


@app.route('/api/metrics/clicks/device', methods=['GET'])
@cache.cached(timeout=1000, query_string=True)
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
@cache.cached(timeout=1000, query_string=True)
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
@cache.memoize(timeout=1000)
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


@app.route("/api/metrics/totalClicks", methods=["GET"])
@cache.cached(timeout=1000, query_string=True)
def getTotalClicks():
    timeframe = request.args.get("timeframe").lower(
    ) if request.args.get("timeframe") is not None else "day"
    timeframe = timeframe if timeframe in ["day", "week", "month"] else "day"
    days = 1 if timeframe == "day" else 7 if timeframe == "week" else 30
    grouping = "format(clicked_date, 'hh tt')" if timeframe == "day"\
        else "format(clicked_date, 'yyyy-MM-dd')" if timeframe == "week"\
        else "format(clicked_date, 'yyyy-MM-dd')"

    cnxn = getConnection()
    cursor = cnxn.cursor()

    res = cursor.execute(f"""
                        declare @latest datetime = (select max(clicked_date) from Events)

                        select count(*),
                            {grouping}
                        from Events
                        where clicked_date > dateadd(day, {-days}, @latest)
                        group by {grouping}
                        order by parse({grouping} as datetime) asc
                        """).fetchall()

    return jsonify(list(map(lambda x: {"period": x[1], "value": x[0]}, res)))


@app.route("/api/metrics/average/<metric>", methods=["GET"])
@cache.memoize(timeout=1000)
def getAverageMetric(metric: str):
    valid_metrics = ["clicksToConvert",
                     "clicksToShare", "timeToConvert", "timeToShare"]
    if metric.lower() not in map(str.lower, valid_metrics):
        return "Invalid metric", 400

    timeframe = request.args.get("timeframe").lower(
    ) if request.args.get("timeframe") is not None else "day"
    timeframe = timeframe if timeframe in ["day", "week", "month"] else "day"
    days = 1 if timeframe == "day" else 7 if timeframe == "week" else 30
    grouping = "format(clicked_date, 'hh tt')" if timeframe == "day"\
        else "format(clicked_date, 'yyyy-MM-dd')" if timeframe == "week"\
        else "format(clicked_date, 'yyyy-MM-dd')"

    cnxn = getConnection()
    cursor = cnxn.cursor()

    res = cursor.execute(f"""
                        declare @latest datetime = (select max(clicked_date) from Events)

                        select avg(cast({metric} as float)),
                            {grouping}
                        from persons_metric
                        left join Events
                        on persons_metric.person_id = Events.person_id
                        where {metric} is not null
                        and clicked_date > dateadd(day, {-days}, @latest)
                        group by {grouping}
                        order by parse({grouping} as datetime) asc
                        """).fetchall()

    return jsonify(list(map(lambda x: {"period": x[1], "value": x[0]}, res)))


@app.route('/api/statistics/time/locale', methods=['GET'])
@cache.cached(timeout=1000, query_string=True)
def statisticsTimeLocale():
    pass


@app.route('/api/statistics/time/device', methods=['GET'])
@cache.cached(timeout=1000, query_string=True)
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
@cache.cached(timeout=1000, query_string=True)
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
@cache.cached(timeout=1000, query_string=True)
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
