from datetime import datetime

def create_persons_metric_table(connection):
    SQL = """                   CREATE TABLE IF NOT EXISTS persons_metric (
                                    person_id INTEGER PRIMARY KEY,
                                    clicksToConvert INTEGER,
                                    clicksToShare INTEGER,
                                    timeToConvert INTEGER,
                                    timeToShare INTEGER,
                                    FOREIGN KEY (person_id) REFERENCES persons (person_id),
                                    UNIQUE(person_id)
                                )
        """
    cursor = connection.cursor()
    cursor.execute(SQL)
    connection.commit()

def insert_persons_metric_table(connection):
    query =                             """SELECT persons.person_id,
                                                events.clicked_date,
                                                persons.master_id,
                                                persons.device,
                                                persons.locale,
                                                events.event_name
                                        from events
                                        INNER JOIN persons
                                        ON persons.person_id = events.person_id
                                        ORDER BY events.clicked_date ASC"""
    cursor = connection.cursor()
    res = cursor.execute(query).fetchall()

    person_id_dict = {}
    for event in res:
        person_id = event[0]
        master_id = event[2]
        time = event[1]
        device = event[3]
        locale = event[4]
        event_name = event[5]

        if person_id not in person_id_dict:
            person_id_dict[person_id] = [[master_id, time, device, locale, event_name]]
        else:
            person_id_dict[person_id].append([master_id, time, device, locale, event_name])
    
    # Computing all the metrics
    persons_list = []
    for person_id in person_id_dict.keys():
        events = person_id_dict[person_id]
        master_id = events[0][0]
        device = events[0][2]
        locale = events[0][3]

        ctc = None
        ttc = None
        counter = 0
        start = datetime.fromisoformat(events[0][1])
        for event in events:
            counter += 1
            if event[4] == 'conversion':
                ctc = counter
                ttc = round((datetime.fromisoformat(event[1]) - start).total_seconds())
                break

        cts = None
        tts = None
        counter = 0
        start = datetime.fromisoformat(events[0][1])
        for event in events:
            counter += 1
            if event[4] == 'share_experience':
                cts = counter
                tts = round((datetime.fromisoformat(event[1]) - start).total_seconds())
                break
            
        persons_list.append([person_id, ctc, ttc, cts, tts])

    SQL = "INSERT INTO persons_metric (person_id, clicksToConvert, timeToConvert, clicksToShare, timeToShare) VALUES (?, ?, ?, ?, ?)"
    cursor.executemany(SQL, persons_list)
    connection.commit()
    
