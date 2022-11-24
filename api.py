from flask import Flask, request, jsonify
import pyodbc

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
	if request.method == 'GET':
		cnxn = pyodbc.connect("""Driver={ODBC Driver 13 for SQL Server};
                        Server=tcp:prenaissance.database.windows.net,1433;
                        Database=customerpp;Uid=alex;Pwd=Test1234;Encrypt=yes;
                        TrustServerCertificate=no;Connection Timeout=30;""")
		cursor = cnxn.cursor()
		res = cursor.execute(f"""SELECT count(*),
							        cast(DATEPART(hour,clicked_date) as int)
									FROM events
									where events.event_name = 'conversion'
									group by cast(DATEPART(hour,clicked_date) as int)""").fetchall()
		print(res)
		cnxn.close()
		return jsonify({'denis':1})
		
if __name__ == '__main__':
	app.run()

