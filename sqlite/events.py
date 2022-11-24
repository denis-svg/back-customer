import sqlite.req as req
from datetime import datetime


def create_events_table(connection):
    sql = f"""               
                                        CREATE TABLE IF NOT EXISTS Events (
                                            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            person_id INTEGER NOT NULL,
                                            event_name TEXT NOT NULL,
                                            clicked_date TIMESTAMP NOT NULL,
                                            urL TEXT NOT NULL,
                                            FOREIGN KEY (person_id) REFERENCES Persons (person_id),
                                            UNIQUE(event_id)
                                        )
            """
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()


def insert_events_table(connection, path):
    data = req.Json.load_json(path)
    cursor = connection.cursor()

    event_list = []
    for entry in data:
        person_id = entry['device_profile_id']
        event_name = entry['event_name']
        time = entry['event_time']
        time = datetime.fromisoformat(time.replace('Z', '-08:00'))
        time += time.utcoffset()
        # time = time.strftime('%Y-%m-%dT%H:%M:%S')
        url = entry['url'].split('?')[0]
        event_list.append([person_id, event_name, url, time])

    SQL = "INSERT INTO events (person_id, event_name, url, clicked_date) VALUES (?, ?, ?, ?)"
    start = 0
    n_chunck = 100
    size_chunk = len(event_list) // n_chunck
    for i in range(n_chunck):
        cursor.executemany(SQL , event_list[start:start + size_chunk])
        connection.commit()
        print(f"""{i + 1} - commit out of {100}""")
        start += size_chunk
    cursor.executemany(SQL , event_list[start:len(event_list)])
    connection.commit()